# helper_tools.py

# MCP integration with Yahoo Finance MCP Server
##   MCP Inspector PORT IS IN USE at http://localhost:6274
##   npx @modelcontextprotocol/inspector yahoo-finance-server  &
##   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=a8a0f131c646a6a5f2a67d792719fc9951995ebf33990fe63cdec182cabdba8c

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
from zoneinfo import ZoneInfo
from dataclasses import dataclass, asdict
import asyncio
from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal, Tuple

## MCP related
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools import google_search, AgentTool, FunctionTool, ToolContext
from mcp import StdioServerParameters
from google.adk.apps.app import App, ResumabilityConfig
from pydantic import BaseModel, Field

## Yahoo Finance MCP Server
import yfinance as yf
from yfinance.const import SECTOR_INDUSTY_MAPPING
from yahoo_finance_server.helper import get_ticker_info, get_ticker_news, search_yahoo_finance, get_top_entities, get_price_history, get_ticker_option_chain, get_ticker_earnings

from . import global_data as gd
from .data_struct import TickerMetadata, TickerMetadataList, StockResearchMetadata, StockData, dataclass_to_pydantic_model

logger = logging.getLogger()

mcp_finance_server = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=gd.MCP_YFIN_COMMAND,
            args=[
            ],
            env={
                'HOME': gd.HOME_DIR,
                'LOGNAME': gd.UNIX_USER_ID,
                'PATH': gd.MCP_YFIN_PATH,
                'SHELL': '/bin/bash',
                'TERM': 'xterm-256color',
                'USER': gd.UNIX_USER_ID
            },
            tool_filter=['get-ticker-info', 'get-top-entities', ],
        ),
        timeout=10,
    )
)

# print('✅ MCP Tool mcp_finance_server created.')

## ******************************************* 
# Define scope levels for state keys (following best practices)
USER_NAME_SCOPE_LEVELS = ("temp", "user", "app")

async def stock_finder_tool(
    entity_type: str, sector_name: str, nos_record: int, sorted_by: str, tool_context: ToolContext,
) -> dict:
    """Get stocks for given entity and sector.

    Args:
        entity_type: Entity type or name
        sector_name: Sector name or description
        nos_record: optional, number of records requsted
        sorted_by: companies sorted by either 'ytd_return' or 'growth_estimate'

    Returns:
        Dictionary with status, message and list of stocks
    """
    logger.info(f'Entering stock_finder_tool with Entity: {entity_type}  Sector: {sector_name}  NosRec: {nos_record} SortBy: {sorted_by}')
    stock_list_dict = None
    try:
        stock_list = list()
        stock_list, ret_msg = await get_stocks_yfin(entity_type, sector_name, nos_record, sorted_by)

#    stock_list = [{"ticker": "APPL", "value": 63636,}, {"ticker": "NVDA", "value": 3463636,}]

        message = f'number of stocks for Entity: {entity_type} and Sector: {sector_name} returned = {len(stock_list)}'
        if len(stock_list) > 0:
            stock_list_dict = {"status": "success", "message": message, "stock_list": stock_list, }
            if tool_context is not None:
                tool_context.state["user:stock_info"] = stock_list_dict
        else:
            message = f'No stocs for Entity: {entity_type} and Sector: {sector_name} were found. {ret_msg}'
            stock_list_dict = {"status": "error", "message": message, "stock_list": [], }

#    tool_context.state["stock_info"] = stock_list_dict
    except Exception as ex:
        stock_list_dict = {"status": "error", "message": ex, "stock_list": [], }

    return stock_list_dict

# print('✅ stock_finder_tool defined')

# returns: symbol and exchange

async def get_symbol_yfin(name: str, count: int = 1) -> Tuple[str, str]:
    logger.info(f'Entering stock_finder_tool. Company name = {name}')
    symbol, exch = ('Symbol missing', 'Exchange missing')
    print(name)
    try:
        info = await search_yahoo_finance(query=name, count=count)
        print(info)
        if info and info['results'] and  info['results'][0]:
                symbol = info['results'][0].get('symbol', 'Symbol missing in Yahoo Finance')
                exch = info['results'][0].get('exchange', 'Exchange missing in Yahoo Finance')
    except Exception as ex:
       symbol = ex

    return (symbol, exch)

async def get_stocks_yfin(entity_type: str, sector: gd.yfin_sectors, count: int, sorted_by: str = 'ytd_return', sort_reverse: bool = False) -> (List[StockData], str):
    try:
        data_list = list()
        message = ''

        info = await get_top_entities(entity_type = entity_type, sector = sector, count = count)
        if info and info['results']:
            entity_type_key = f'top_{entity_type}'
            entity, sect, industry = (info['entity_type'], info['sector'], '')
            if entity_type in ['growth_companies', 'performing_companies']:
                    for item in info['results']:
                        industry = item['industry']
                        cm_list = ast.literal_eval(item[entity_type_key].replace(":null",''':0.0'''))
                        for item_cm in cm_list:
                            est = item_cm['growth estimate'] if item_cm.get('growth estimate') is not None else item_cm.get(' growth estimate', 0.0)
                            name, ytd, = (item_cm['name'], item_cm['ytd return'], )
                            (symbol, exch) = await get_symbol_yfin(name, 1)
                            data_list.append(StockData(entity, sect, industry, name, ytd, est, symbol, exch))
            else:
                for item in info['results']:
                    name, est, ytd = item, 0.0, 0.0
                    (symbol, exch) = await get_symbol_yfin(name, 1)
                    data_list.append(StockData(entity, sect, industry, name, ytd, est, symbol, exch))
### Get Ticker from ShortName
            

        if len(data_list) > 0:
            data_list.sort(key=lambda item: getattr(item, sorted_by), reverse=not sort_reverse)
            return data_list[0:count], message
    except Exception as ex:
        message = f'( Error: {ex} )'
        data_list = list()

    return data_list, message
# print('✅ get_stocks_yfin for use in tool defined')

def stock_finder_error(
    entity_type: str, sector_name: str, nos_record: int, sorted_by: str, tool_context: ToolContext,
) -> dict:
    """Checks validity of entity type, sector, nos of records.

    Args:
        entity_type: Entity type or name
        sector_name: Sector name or description
        nos_record: optional, number of records requsted
        sorted_by: companies sorted by either 'ytd_return' or 'growth_estimate'

    Returns:
        Dictionary with status, message and list of stocks
    """
    logger.info(f'Entering stock_finder_error with Entity: {entity_type}  Sector: {sector_name}  NosRec: {nos_record} SortBy: {sorted_by}')

    stock_list = list()
    message = None
    stock_list_dict = None

    try:
        yfin_entity_type_list = list(gd.yfin_entity_type.__args__)
        yfin_sectors_list = list(gd.yfin_sectors.__args__)

        if entity_type not in yfin_entity_type_list:
            message = f'Validation failed for Entity type {entity_type}. Enter one of: {", ".join(yfin_entity_type_list)}'
            stock_list_dict = {"status": "error", "message": message, "stock_list": stock_list, }
        elif sector_name not in yfin_sectors_list:
            message = f'Validation failed for Sector {sector_name}. Enter one of: {", ".join(yfin_sectors_list)}'
            stock_list_dict = {"status": "error", "message": message, "stock_list": stock_list, }
        elif sorted_by not in ['ytd_return', 'growth_estimate']:
            message = f'Validation failed for Sorted By {entity_type}, Sector name {sector_name}, Sorted by {sorted_by}: Error Message - Valid values: ytd_return, growth_estimate'
            stock_list_dict = {"status": "error", "message": message, "stock_list": stock_list, }
        elif nos_record < 1 or nos_record > 20:
            message = f'Validation failed for Entity type {entity_type}, Sector name {sector_name}, Nos record {nos_record}: Error Message - Nos of record should be no more than 20'
            stock_list_dict = {"status": "error", "message": message, "stock_list": stock_list, }
        else:
            message = f'Validation successful for Entity type {entity_type}, Sector name {sector_name}, Nos record {nos_record}'
            stock_list_dict = {"status": "success", "message": message, "stock_list": stock_list, }
            tool_context.state["user:stock_info"] = stock_list_dict
    except Exception as ex:
        stock_list_dict = {"status": "error", "message": ex, "stock_list": [], }

    return stock_list_dict
# print('✅ stock_finder_error defined')

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


async def symbol_finder_tool(company_name: str) -> dict:  ## quarterly or annual
    """Get Symbol or Ticker for a company name.

        Args:
            company_name: name of the company 

        Returns:
            Dictionary with status, message and dictionary with symbol and exchange
    """

    earnings_str = 'Symbol missing or invalid'
    en_dct = None
    try:
        (symbol, exch) = await get_symbol_yfin(name=company_name, count=1)
#        print(f'Type = {type(info)}   Length = {len(info)}')
        if symbol and exch:
            symbl_dct = {'company_name': company_name, 'symbol': symbol, 'exchange': exch,}
            en_dct = {'status': 'success', 'message': '', 'symbol_data' : symbl_dct}
        else:
            symbl_dct = {'company_name': company_name, 'symbol': '', 'exchange': '',}
            en_dct = {'status': 'error', 'message': f'Either symbol or exchange missing {symbol} {exch}', 'symbol_data' : symbl_dct}
    except Exception as ex:
        symbl_dct = {'company_name': company_name, 'symbol': '', 'exchange': '',}
        en_dct = {'status': 'error', 'message': f'Tool returned error: {ex}', 'symbol_data' : symbl_dct}

#    print(f'Earnings = {en_dct}')
    return en_dct

def entity_finder_tool(tool_context: ToolContext, ) -> dict:
    '''To get list of Entity Types.

    Args:
    None

    Returns:
        Dictionary with status and message with list of Entity Types.
    '''

    try:
        msg = f'List of Entity types: {", ".join(list(gd.yfin_entity_type.__args__))}'
        return {'status' : 'success', 'message': msg}
    except Exception as ex:
        return {'status' : 'error', 'message': ex}


def sector_finder_tool(tool_context: ToolContext, ) -> dict:
    '''To get list of Sector Names.

    Args:
    None

    Returns:
        Dictionary with status and message with list of Sector Names.
    '''

    try:
        msg = f'List of Sector names: {", ".join(list(gd.yfin_sectors.__args__))}'
        return {'status' : 'success', 'message': msg}
    except Exception as ex:
        return {'status' : 'error', 'message': ex}


# print('✅ Function Tools entity_finder_tool and sector_finder_tool defined.')
