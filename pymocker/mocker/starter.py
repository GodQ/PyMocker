import asyncio
import requests
import os
from pathlib import Path
from colorama import Fore

from pymocker.config import config
from pymocker.lib.log import get_logger
from pymocker.mocker.proxy_run import mitmweb
from pymocker.mocker.rules import current_mock_server, refresh_settings_from_remote

"""
HTTP proxy server
"""

CURRENT_PATH = Path(__file__).parent
FLOW_PATH = CURRENT_PATH / 'mitm.py'

logger = get_logger()


def run_mocker(reverse_target_url, mock_port, mock_web_port):
    logger.warning(f'Proxy starts on 0.0.0.0:{mock_port}   {Fore.CYAN}')
    # mitm_arguments = [
    #     '-s', str(FLOW_PATH),
    #     '-p', self.proxy_port,
    #     '--ssl-insecure',
    #     '--no-http2',
    #     '-q'
    # ]
    # if self.ignore_hosts:
    #     mitm_arguments += ['--ignore-hosts', self.ignore_hosts]
    # run(DumpMaster, mitmdump, mitm_arguments)
    mitm_arguments = [
        '-s', str(FLOW_PATH),
        '--mode', f'reverse:{reverse_target_url}',
        '--listen-port', str(mock_port),
        '--web-port', str(mock_web_port),
        '--web-host', '0.0.0.0',
        '--no-web-open-browser',
        '--showhost',
        '-vvvvvv',
        '--ssl-insecure',
        '--no-http2',
        # '-q'
    ]
    print(mitm_arguments)
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    mitmweb(mitm_arguments)


def start(mock_server_id=None):
    if not mock_server_id:
        mock_server_id = os.environ.get('mock_server_id', None)
    print("Starting Mock Server", mock_server_id)
    assert mock_server_id
    # mgmt_url = f'http://{config.mgmt_host}:{config.mgmt_port}/mock_servers/{mock_server_id}'
    # resp = requests.get(mgmt_url)
    # print("Fetch mock server config from mgmt, status: ", mock_server_id, resp.status_code, resp.reason, resp.content)
    # assert resp.status_code == 200, f'{mgmt_url}, {resp.status_code}, {resp.reason}, {resp.content}'
    # settings = resp.json()
    # current_mock_server.load(settings)
    settings = refresh_settings_from_remote(mock_server_id)
    print(settings)
    os.environ['mock_port'] = str(settings['mock_port'])
    os.environ['mock_web_port'] = str(settings['mock_web_port'])
    os.environ['target_url'] = settings['target_url']
    run_mocker(reverse_target_url=settings['target_url'],
               mock_port=settings['mock_port'],
               mock_web_port=settings['mock_web_port'])


if __name__ == '__main__':
    start('001')
