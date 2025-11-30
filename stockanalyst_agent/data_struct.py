# data_struct.py

## MCP related imports
import ast
from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal, Tuple
from dataclasses import dataclass, asdict

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.apps.app import App, ResumabilityConfig
from pydantic import BaseModel, Field

## Yahoo Finance MCP Server imports
import yfinance as yf
from yfinance.const import SECTOR_INDUSTY_MAPPING
from yahoo_finance_server.helper import get_ticker_info, get_ticker_news, search_yahoo_finance, get_top_entities, get_price_history, get_ticker_option_chain, get_ticker_earnings


class TickerMetadata(BaseModel):   # 'sector', 'company name', 'current price', 'P/E ratio', 'market cap' 
    ticker: str = Field(description='ticker symbol')
    sector: str = Field(description='sector of the industry')
    industry: Optional[str] = Field('', description='optional name of the industry')
    name: str = Field(description='name of the company')
    market_cap: Optional[float] = Field(0.0, description='Optional Market Capitalization in USD')
    current_price: float = Field(description='Current Price')
    pe_ratio: Optional[float] = Field(0.0, description='Optional Forward P/E ratio - price per earning ratio')
# print('✅ Pydantic class TickerMetadata created')

class TickerMetadataList(BaseModel):
    tickerlist: List[TickerMetadata]
# print('✅ Pydantic class TickerMetadataList created')

class StockResearchMetadata(BaseModel):
    status: str = Field(description='status returned from tool, either success or failure')
    message: str = Field(description='status message from tool')
    tickerlist: List[Dict]

@dataclass
class StockData:
    entity_type: str
    sector: str
    industry: str
    name: str
    ytd_return: float
    growth_estimate: float
    symbol: str
    exchange: str

    def getAsDict(self) -> Dict:
        return asdict(self)
    def camel_case_converter(value: str):
        parts = value.lower().split('_')
        return parts[0] + ''.join(i.title() for i in parts[1:])

def dataclass_to_pydantic_model(kls: Type[dataclass]) -> Type[BaseModel]:
    """Converts a standard dataclass to a Pydantic BaseModel."""
    class BaseModelDataclass(BaseModel, kls):
        pass
    return BaseModelDataclass

# StockDataMetaData: BaseModel = dataclass_to_pydantic_model(StockData)
# test_dc = StockData("growth_companies", "technology", "software-application", "Xperi Inc.", -0.4469, 80.0)
# test_dct = test_dc.getAsDict()
# print(test_dct)

# print('✅ Pydantic class StockResearchMetadata, Standard dataclass StockData created')
