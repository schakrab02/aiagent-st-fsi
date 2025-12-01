# global_date.py

from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal
from google.genai import types

from .common_utils import setget_env_var

UNIX_USER_ID = setget_env_var('LOCAL_USER')
HOME_DIR = setget_env_var('LOCAL_HOME')
# MCP_YFIN_TARGET_FOLDER_PATH = f'{HOME_DIR}/drsa/mcp-yahoo'
MCP_YFIN_PATH = f'{HOME_DIR}.npm/_npx/5a9d879542beca3a/node_modules/.bin:{HOME_DIR}/drsa/venv/bin'
MCP_YFIN_COMMAND = 'yahoo-finance-server'

# MODEL_NAME = 'gemini-2.5-flash-lite'
MODEL_NAME = 'gemini-2.5-flash'

TRADING_AUTO_APPROVAL_LIMIT = 2
TRADING_MAXIMUM_LIMIT = 1000

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

yfin_entity_type = Literal[
        'etfs', 'mutual_funds', 'companies', 'growth_companies', 'performing_companies'
    ]

yfin_sectors = Literal[
    'basic-materials',
    'communication-services',
    'consumer-cyclical',
    'consumer-defensive',
    'energy',
    'financial-services',
    'healthcare',
    'industrials',
    'real-estate',
    'technology',
    'utilities',
]

# logger.info(f'✅ retry_config = {retry_config}')
# print('✅ Data: retry_config, yfin_entity_type, yfin_sectors define successfully.')
