# common_utils.py

import os
import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import getpass

def setget_env_var(var: str) -> str:
    if not os.environ.get(var):
        os.environ[var] = getpass(f'Enter your {var}: ')
    return os.environ[var]


# Clean up any previous logs
def setup_logger(logfile_name: str = 'earnings-remote-agent.log'):
# Clean up any previous logs
#    for log_file in ['logger.log', 'web.log', 'tunnel.log']:
#        if os.path.exists(log_file):
#            os.remove(log_file)
#            print(f'🧹  Cleaned up {log_file}')

    load_dotenv()

# Configure logging with INFO log level.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
#    logging.basicConfig(filename='logger.log', level=logging.DEBUG, format='%(filename)s:%(lineno)s %(levelname)s:%(message)s',)
    file_handler = RotatingFileHandler(logfile_name, mode='a', delay=True, maxBytes=250000, backupCount=3)
#    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s %(levelname)s : %(message)s'))
    logger.addHandler(file_handler)

#    strt_run_raw = datetime.now(ZoneInfo('America/New_York'))
    strt_run = datetime.now(ZoneInfo('America/New_York')).strftime('%Y-%m-%dT%H:%M:%S%z')

    logger.info(f'\n\n New Run started at {strt_run}')

def setup_logger_NA(logfile_name: str = 'stock-agent'):
# Configure logging with DEBUG log level.
    logging.basicConfig(
        filename='logger.log',
        level=logging.DEBUG,
        format='%(filename)s:%(lineno)s %(levelname)s:%(message)s',
    )
    logger = logging.getLogger(__name__)
##print(logger)
    logger.info(f'Logging configured')

setup_logger('earnings-remote-agent.log')

