# agent.py

from google.adk.agents.llm_agent import Agent

import logging
import os
import subprocess
import time
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
from zoneinfo import ZoneInfo
from dataclasses import dataclass, asdict
import asyncio
from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal, Tuple

from google.genai import types
from google.adk.models.google_llm import Gemini
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent, LlmAgent
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService, Session
from google.adk.tools import google_search, AgentTool, FunctionTool, ToolContext
# from google.adk.tools.function_tool import FunctionTool
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.apps.app import App, EventsCompactionConfig
# from google.adk.tools.agent_tool import AgentTool
# from google.adk.tools.google_search_tool import google_search

## Yahoo Finance MCP Server
import yfinance as yf
from yfinance.const import SECTOR_INDUSTY_MAPPING
from yahoo_finance_server.helper import get_ticker_info, get_ticker_news, search_yahoo_finance, get_top_entities, get_price_history, get_ticker_option_chain, get_ticker_earnings

from google.adk.agents.remote_a2a_agent import (
    RemoteA2aAgent,
    AGENT_CARD_WELL_KNOWN_PATH,
    )
from google.adk.a2a.utils.agent_to_a2a import to_a2a
# from google.adk.agents.wrapper import to_a2a


from . import global_data as gd
from .common_utils import setup_logger

setup_logger('earnings-remote-agent.log')


async def earnings_finder_tool(symbol: str, period: str = 'quarterly') -> dict:  ## quarterly or annual
    """Get stocks for given entity and sector.

        Args:
            symbol: stock symbol or ticker name
            period: optional, earnings period, either 'annual' or 'quarterly'

        Returns:
            Dictionary with status, message and list of earnings
    """

    earnings_str = 'Symbol missing or invalid'
    en_dct = None
    try:
        info = await get_ticker_earnings(symbol=symbol, period=period)
#        print(f'Type = {type(info)}   Length = {len(info)}')
        if info and info['earnings_data'] and len(info['earnings_data']) > 0:
            en_dct = {'status': 'success', 'message': '', 'earning_list' : info['earnings_data']}
        else:
            en_dct = {'status': 'error', 'message': earnings_str, 'earning_list' : []}
    except Exception as ex:
        earnings_str = f'{earnings_str}.  Error: {ex}'
        en_dct = {'status': 'error', 'message': earnings_str, 'earning_list' : []}

#    print(f'Earnings = {en_dct}')
    return en_dct



# Remote Agent: Create earnings agent using API from Yahoo Finance
#   uvicorn agent:a2a_app --host localhost --port 8001
earnings_remote_agent = LlmAgent(
    model=Gemini(model=gd.MODEL_NAME, retry_options=gd.retry_config),
    name='earnings_remote_agent',
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

    Save Session state to 'earnings_result'
    ''',
    tools=[FunctionTool(func=earnings_finder_tool)],
#    output_schema=TickerMetadataList,
    output_key='earnings_result',  # The result of this agent will be stored in the session state with this key.
)
# Wrap your agent with to_a2a()
wrapped_agent = to_a2a(earnings_remote_agent)

a2a_app = to_a2a(
    earnings_remote_agent, port=8001  # Port where this agent will be served
    )


