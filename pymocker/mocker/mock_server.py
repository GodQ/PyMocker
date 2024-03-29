import time
import asyncio
import json
from pathlib import Path
from colorama import Fore, Style
from pymocker.mocker.proxy_run import mitmweb
from pymocker.mgmt.port_repo import PortRepo
from pymocker import config
from pymocker.lib.log import get_logger
from pymocker.lib.utils import get_host_ip


"""
HTTP proxy server
"""

CURRENT_PATH = Path(__file__).parent
FLOW_PATH = CURRENT_PATH/'mitm.py'


logger = get_logger()
current_mock_server = None


class MockServer:

    def __init__(self,
                 mock_port: int = None,
                 mock_web_port: int = None,
                 reverse_target_url: str = None,
                 mock_server_id: str = None,
                 mock_rules: list = None,
                 host: str = None):
        super().__init__()
        self.reverse_target_url = reverse_target_url
        if self.reverse_target_url.split(':')[0] == 'https':
            self.url_schema = 'https'
        else:
            self.url_schema = 'http'
        self.mock_rules = mock_rules
        if host:
            self.host = host
        else:
            self.host = get_host_ip()

        if not mock_port:
            self.mock_port = PortRepo.find_available_port()
        else:
            mock_port = int(mock_port)
            port_available = PortRepo.check_port_available(mock_port)
            if port_available is False:
                raise Exception(f"The mock_port {mock_port} is in use")
            self.mock_port = mock_port
        if not mock_web_port:
            self.mock_web_port = PortRepo.find_available_port()
        else:
            mock_web_port = int(mock_web_port)
            port_available = PortRepo.check_port_available(mock_web_port)
            if port_available is False:
                raise Exception(f"The mock_web_port {mock_web_port} is in use")
            self.mock_web_port = mock_web_port
        if not mock_server_id:
            self.mock_server_id = str(time.time())
        else:
            self.mock_server_id = mock_server_id
        '''
        --ignore_hosts:
        The ignore_hosts option allows you to specify a regex which is matched against a host:port
        string (e.g. “example.com:443”) of a connection. Matching hosts are excluded from interception,
        and passed on unmodified.
        # Ignore everything but sankuai.com, meituan.com and dianping.com:
        --ignore-hosts '^(?!.*sankuai.*)(?!.*meituan.*)(?!.*dianping.*)'
        According to mitmproxy docs: https://docs.mitmproxy.org/stable/howto-ignoredomains/
        '''
        # self.ignore_hosts = None
        # if conf.get('proxy.filters'):
        #     self.ignore_hosts = '^%s' % ''.join(['(?!.*%s.*)' % i for i in conf.get('proxy.filters')])

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d)

    def to_dict(self):
        d = {
            "target_url": self.reverse_target_url,
            "mock_port": self.mock_port,
            "mock_web_port": self.mock_web_port,
            "mock_server_id": self.mock_server_id,
            # "process_id": self.get_pid(),
            "mock_rules": self.mock_rules,
            "access_url": self.get_access_url(),
            "monitor_web_url": self.get_monitor_url()
        }
        return d

    def get_access_url(self):
        return f"{self.url_schema}://{self.host}:{self.mock_port}"

    def get_monitor_url(self):
        return f"http://{self.host}:{self.mock_web_port}"

    def run(self):
        global current_mock_server
        current_mock_server = self
        proxy_ip = str(config.config.proxy_host)
        logger.warning(f'Proxy starts on http://{proxy_ip}:{self.mock_port}   {Fore.CYAN}')
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
            '--mode', f'reverse:{self.reverse_target_url}',
            '--listen-port', str(self.mock_port),
            '--web-port', str(self.mock_web_port),
            '--web-host', proxy_ip,
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


# proxy_server = ProxyServer()


def info_msg(*msg):
    print(f'{Fore.YELLOW}[proxy_server]', *msg, Style.RESET_ALL)


if __name__ == '__main__':
    server = MockServer()
    server.start()
