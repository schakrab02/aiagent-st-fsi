# agent.py

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from contextlib import suppress
import uuid
import sys
import json
import ast
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal
from dataclasses import dataclass, asdict
import asyncio

from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent, LlmAgent
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService, Session
from google.adk.tools import google_search, AgentTool, FunctionTool, ToolContext
# from google.adk.tools.function_tool import FunctionTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.apps.app import App, EventsCompactionConfig, ResumabilityConfig
from google.adk.agents.remote_a2a_agent import ( RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH,)
# from google.adk.tools.agent_tool import AgentTool
# from google.adk.tools.google_search_tool import google_search
import vertexai

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    )
# print(f'{os.environ["GOOGLE_CLOUD_PROJECT"]}  {os.environ["GOOGLE_CLOUD_LOCATION"]}')
##  exit()

from .helper_tools import mcp_finance_server, stock_finder_tool, stock_finder_error, entity_finder_tool, sector_finder_tool, earnings_finder_tool, symbol_finder_tool, request_trading_order
from .data_struct import TickerMetadata, TickerMetadataList, StockResearchMetadata, StockData, dataclass_to_pydantic_model

from . import global_data as gd
# from google.adk.runners import App
from .observability_plugin import ObservabilityPlugin


## Definition of Root Agent and knitting together Other Agents.

### HITL:  https://github.com/google/adk-docs/blob/main/examples/python/snippets/tools/function-tools/human_in_the_loop.py

MODEL_NAME = 'gemini-2.5-flash-lite'

# Agent-1: Research agent with pausable tool
#    To provide list of Entity Types, use 'entity_finder_tool'.
#    To provide list of Sector Names, use 'sector_finder_tool'.
#    To provide Symbol and Exchange, use 'symbol_finder_tool' passing company name to the tool.
query_agent = LlmAgent(
    name='query_agent',
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    instruction="""
    You are a Smart Tool calling assistant to provide list of Entity types or list of Sector names or symbol for a given company name.
    To provide list of Entity Types, use 'entity_finder_tool'.
    To provide list of Sector Names, use 'sector_finder_tool'.
    To provide Symbol and Exchange, use 'symbol_finder_tool' passing company name to the tool.

    You can only use 'entity_finder_tool' tool or 'sector_finder_tool' tool or 'symbol_finder_tool' tool.
    You are not allowed to use other tool or search the WEB.
  """,
    tools=[FunctionTool(func=entity_finder_tool), FunctionTool(func=sector_finder_tool), FunctionTool(func=symbol_finder_tool), ],
    output_key='query_result',  # The result of this agent will be stored in the session state with this key.
)

# print('✅ Query Agent created.')

# Agent-2: Create stockdetail agent using MCP integration
stockdetail_agent = LlmAgent(
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    name='stockdetail_agent',
    instruction='''
    You are ticker search agent using the MCP Tool to get ticker information for one or more ticker provide to you.
    Save Session state to 'stockdetail_result'

    IMPORTANT: Always return your response as a JSON object inside a python list with the following structure:
    {
        'ticker': 'ticker or symbol',
        'sector': 'sector of the industry',
        'industry': 'industry that company belongs to',
        'name': 'company name',
        'market_cap': 'Market Capitalization',
        'current_price': 'Current Price',
        'pe_ratio': 'ForwardPE'
    }
    ''',
    tools=[mcp_finance_server],
    output_schema=TickerMetadataList,
    output_key='stockdetail_result',  # The result of this agent will be stored in the session state with this key.
)

# print('✅ StockDetail Agent created.')

# Agent-3: Create research agent with pausable tool
research_agent = LlmAgent(
    name='research_agent',
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    instruction="""
    You are a Smart Tool calling assistant to find stocks. You can only use 'stock_finder_error' tool and 'stock_finder_tool' tool.

    When user provides input,
    First, Use the 'stock_finder_error' tool for validation, passing entity type, sector name, number of stocks and order by asked .
    If status returned is "error", do not call any other tool. Otherwise, Use the 'stock_finder_tool' tool passing entity type, sector name, number of stocks and order by asked.

    You are not allowed to use other tool or search the WEB.

    Your response should be a python dictionary from the function tool.

  """,
    tools=[FunctionTool(func=stock_finder_tool), FunctionTool(func=stock_finder_error), ],
    output_key='research_result',  # The result of this agent will be stored in the session state with this key.
)

# print('✅ Research Agent created.')

# Agent-4: Generic WEB search agent
web_search_agent = LlmAgent(
    name='web_search_agent',
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    description='A simple agent that can answer general questions using Google earch tool.',
    instruction='''You are a helpful information technoloy assistant. Use Google Search for current info or if unsure.
    Your only job is to use the google_search tool to provide brief technical summary in 4-5 sentenses with relevant information 
    on the given topic. Please be precise and to the point.
    ''',
    tools=[google_search],
    output_key='web_search_result',  # The result of this agent will be stored in the session state with this key.
)

# Agent-5 (Local Agent): Create earnings agent using API from Yahoo Finance
earnings_local_agent = LlmAgent(
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    name='earnings_local_agent',
    instruction='''
    You are earnings lookup agent using the Function Tool 'earnings_finder_tool' to get quarterly earnings. 
    You will be given a symbol or ticker as input'.

    IMPORTANT: Always return your response as a JSON object inside a python list with the following structure:
    {
        'Date': 'period end date as string yyyy-mm-dd format',
        'Total Revenue': 'total revenue in this period in number',
        'Gross Profit': 'gross profit in this period in number',
        'Operating Income': 'operating incomde in this period in number',
        'Net Income': 'net incomde in this period in number',
        'EBIDTA': 'earnings before interst, depreciation, tax and amortization in this period in number',
    }

    Save Session state to 'earnings_result'
    ''',
    tools=[FunctionTool(func=earnings_finder_tool)],
#    output_schema=TickerMetadataList,
    output_key='earnings_result',  # The result of this agent will be stored in the session state with this key.
)

# Agent-6 (Remote Agent): Create earnings agent using API from Yahoo Finance
earnings_remote_agent = RemoteA2aAgent(
    name="earnings_remote_agent",
    description="Remote earnings agent from Accounting Department to get earnings of a period.",
    # Point to the agent card URL - this is where the A2A protocol metadata lives
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    )

earnings_agent = LlmAgent(
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    name='earnings_agent',
    instruction='''
    You are earnings lookup agent using the Function Tool 'earnings_finder_tool' to get earnings of a period. 
    You will be given a symbol or ticker as input'.

    IMPORTANT: Always return your response as a JSON object inside a python list with the following structure:
    {
        'Date': 'period end date as string yyyy-mm-dd format',
        'Total Revenue': 'total revenue in this period in number',
        'Gross Profit': 'gross profit in this period in number',
        'Operating Income': 'operating incomde in this period in number',
        'Net Income': 'net incomde in this period in number',
        'EBIDTA': 'earnings before interst, depreciation, tax and amortization in this period in number',
    }

    ''',
    sub_agents=[earnings_remote_agent],
#    output_schema=TickerMetadataList,
    output_key='earnings_result',  # The result of this agent will be stored in the session state with this key.
)

# Agent-7: Create research agent with pausable tool
review_summary_agent = LlmAgent(
    name='Review_Summary_Agent',
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    instruction="""
    You are a Smart Agent to write a summary report for investment user.
   
    To summarize, please use information ONLY from {stockdetail_result} and {earnings_result}. 
    You are NOT ALLOWED to make any web search or use any other tool.

    Your response should be concise, professional and brief. Your response should be less than 300 words.

  """,
    output_key='review_summary_result',  # The result of this agent will be stored in the session state with this key.
)

# The ParallelAgent runs all its sub-agents simultaneously.
parallel_analysis_agent = ParallelAgent(
    name="Parallel_Analysis_Agent",
    sub_agents=[stockdetail_agent, earnings_local_agent,],
    )

analysis_agent = SequentialAgent(
    name="Analysis_Agent",
    sub_agents=[parallel_analysis_agent, review_summary_agent],
    )

## Trading Agent
trading_agent = LlmAgent(
    name="trading_agent",
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    instruction="""You are a trading request and approval coordinator assistant.
                      
    When users request to Buy or Sell with a specified number of stock or symbol or ticker:

    Send your response with status and message from the tool.
""",
    tools=[FunctionTool(func=request_trading_order)],
    )

'''
    1. Use the request_trading_order tool with Buy or Sell, and the number of stock or symbol or ticker.
    2. If the order status is 'pending', inform the user that approval is required with a message returned from request_trading_order tool.
    3. If the order status is 'approved', inform the user that approval is obtained and order is ready for execution with a message returned from request_trading_order tool.
    4. If the order status is 'rejected', inform the user that approval is rejected with a message returned from request_trading_order tool.
    5. After receiving the result, provide a clear summary. 
    6. Keep responses concise but informative


        - Order status (approved/rejected)
        - Symbol 
        - Price (if available)
        - Side, either 'Buy' or 'Sell'
        - Number of stock or symbol or ticker 
'''
## ROOT AGENT: This is essentially a routing agent.
root_agent = LlmAgent(
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    name='stock_analysis_agent',
    instruction='''
    You are Stock Analyst routing agent for stock analysis using tools provided to you.
    1. Use 'query_agent' tool, if you are asked to provide for list of entity type or list of sector name or symbol for a company name. For research and summarize, please use sub agent 'analysis_agent'.
    2. Use 'stockdetail_agent' tool, if you are asked to provide information for specifc company name or stock ticker symbol. For research and summarize, please use sub agent 'analysis_agent'.
    3. Use 'research_agent' tool, if you are asked to provide list of stocks for given entity type, sector name, and number of records.  For research and summarize, please use sub agent 'analysis_agent'.
    4. Use 'earnings_agent' tool, if you are asked to provide earnings information for symbol or ticker name. User may optionally provide period either 'annual' or 'quarterly'. For research and summarize, please use sub agent 'analysis_agent'.
    5. Use sub-agent 'analysis_agent', if you are asked to reseach and summarize for specific symbol or ticker.
    6. Use 'trading_agent', if you are asked to Buy or Sell with number of stocks for a symbol. Call the tool with three parameters, Symbol, buy or sell, number of orders.. For example, Buy 10 stocks for symbol MSFT. For example, Please sell 25 stocks of NVDA
    7. Use 'web_search_agent' tool for all other user queries.    
    ''' ,
    tools=[AgentTool(agent=query_agent), AgentTool(agent=stockdetail_agent), AgentTool(agent=research_agent), 
        AgentTool(agent=earnings_agent), AgentTool(agent=trading_agent), AgentTool(agent=web_search_agent), ],
    sub_agents=[analysis_agent, ],
    output_key='analysis_result'  # The result of this agent will be stored in the session state with this key.
)
# app = App( name="stockanalyst_app", root_agent=root_agent, plugins=[ObservabilityPlugin()],  # Add your custom plugin here)

obsv_plugin = ObservabilityPlugin()

app = App(
    name="stockanalyst_agent",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
          compaction_interval=30,   # Trigger compaction every 5 invocations
          overlap_size=3,  # Keep 2 previous turn for context,
          ),
    plugins=[obsv_plugin],  # Add your custom plugin here
    resumability_config=ResumabilityConfig(is_resumable=True),
    )
# Register the plugin with the Runner
# Credit: https://github.com/google/adk-python/issues/3522
# runner = InMemoryRunner( agent=root_agent, plugins=[obsv_plugin],)

async def setup_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name='stockanalyst_app', user_id=gd.UNIX_USER_ID)

    app = App(
        name="stockanalyst_app",
        root_agent=root_agent,
        events_compaction_config=EventsCompactionConfig(
          compaction_interval=30,   # Trigger compaction every 5 invocations
          overlap_size=3,  # Keep 2 previous turn for context,
          ),
###        plugins=[ObservabilityPlugin()],  # Add your custom plugin here
        )

    runner = Runner(app=app, session_service=session_service)
    await runner.run(session=session)

# asyncio.run(setup_runner())

# print('✅ Analyst Agent (for routing) created.')
