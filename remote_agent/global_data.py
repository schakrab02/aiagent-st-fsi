# global_date.py

from typing import Type, Dict, Any, Optional, List, Union, Annotated, Literal
from google.genai import types

from .common_utils import setget_env_var

MODEL_NAME = 'gemini-2.5-flash-lite'

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
#
