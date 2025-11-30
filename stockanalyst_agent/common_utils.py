# common_utils.py

import os
import logging
import getpass
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# from IPython.display import display, HTML
# from jupyter_server.serverapp import list_running_servers


def setget_env_var(var: str) -> str:
    if not os.environ.get(var):
        os.environ[var] = getpass(f'Enter your {var}: ')
    return os.environ[var]


# Clean up any previous logs
def setup_logger(logfile_name: str = 'stock-agent.log'):
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
    file_handler = RotatingFileHandler(logfile_name, mode='a', delay=True, maxBytes=100000, backupCount=8)
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

setup_logger('stock-agent.log')

#logger = logging.getLogger(__name__)
#print(f'✅ Logging configured with Logger {__name__}  {logging.getLogger(__name__)}')

# Gets the proxied URL in the Kaggle Notebooks environment
"""
def get_adk_proxy_url():
#    PROXY_HOST = 'https://kkb-production.jupyter-proxy.kaggle.net'
#    ADK_PORT = '8000'
    PROXY_HOST = 'localhost'
    ADK_PORT = '8000'

    servers = list(list_running_servers())
    if not servers:
        raise Exception('No running Jupyter servers found.')

#   baseURL = servers[0]['base_url']
#
#    try:
#        path_parts = baseURL.split('/')
#        kernel = path_parts[2]
#        token = path_parts[3]
#    except IndexError:
#        raise Exception(f'Could not parse kernel/token from base URL: {baseURL}')


#    print(servers)
    baseURL = servers[0]['base_url']
#    print(baseURL)
    serverURL = servers[0]['url']
#    print(serverURL)

    try:
        path_parts = baseURL.split('/')
        print(len(path_parts))
        if len(path_parts) <= 2:
            path_parts = serverURL.split('/')
            print(path_parts)
        kernel = path_parts[2]
        token = path_parts[3]
    except IndexError:
        raise Exception(f'Could not parse kernel/token from base URL: {baseURL}')

    url_prefix = f'/k/{kernel}/{token}/proxy/proxy/{ADK_PORT}'
    url = f'{PROXY_HOST}{url_prefix}'

    styled_html = f'''
    <div style='padding: 15px; border: 2px solid #f0ad4e; border-radius: 8px; background-color: #fef9f0; margin: 20px 0;'>
        <div style='font-family: sans-serif; margin-bottom: 12px; color: #333; font-size: 1.1em;'>
            <strong>⚠️ IMPORTANT: Action Required</strong>
        </div>
        <div style='font-family: sans-serif; margin-bottom: 15px; color: #333; line-height: 1.5;'>
            The ADK web UI is <strong>not running yet</strong>. You must start it in the next cell.
            <ol style='margin-top: 10px; padding-left: 20px;'>
                <li style='margin-bottom: 5px;'><strong>Run the next cell</strong> (the one with <code>!adk web ...</code>) to start the ADK web UI.</li>
                <li style='margin-bottom: 5px;'>Wait for that cell to show it is 'Running' (it will not 'complete').</li>
                <li>Once it's running, <strong>return to this button</strong> and click it to open the UI.</li>
            </ol>
            <em style='font-size: 0.9em; color: #555;'>(If you click the button before running the next cell, you will get a 500 error.)</em>
        </div>
        <a href='{url}' target='_blank' style='
            display: inline-block; background-color: #1a73e8; color: white; padding: 10px 20px;
            text-decoration: none; border-radius: 25px; font-family: sans-serif; font-weight: 500;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: all 0.2s ease;'>
            Open ADK Web UI (after running cell below) ↗
        </a>
    </div>
    '''

    display(HTML(styled_html))

    return url_prefix
"""

# logger.info(f'url_prefix')

# print('✅ Helper functions defined.')
