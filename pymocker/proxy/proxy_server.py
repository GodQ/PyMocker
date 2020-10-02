import socket
import asyncio
import json
from pathlib import Path
from colorama import Fore, Style
from pymocker.proxy.proxy_run import run, mitmweb
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.cmdline import mitmdump
from pymocker.base_server import ProcessServer
from pymocker import settings
from pymocker.log import get_logger


"""
HTTP proxy server
"""

CURRENT_PATH = Path(__file__).parent
FLOW_PATH = CURRENT_PATH/'mitm.py'


logger = get_logger()
current_proxy_server = None


class ProxyServer(ProcessServer):

    def __init__(self, proxy_port=80, proxy_web_port=8086, reverse_proxy_url="https://www.baidu.com", proxy_id=None,
                 proxy_settings=None):
        super().__init__()
        self.reverse_proxy_url = reverse_proxy_url
        self.proxy_settings = proxy_settings

        conf = settings.config
        self.proxy_ip = str(conf.proxy_host)
        if not proxy_port:
            self.proxy_port = str(conf.proxy_port)
        else:
            self.proxy_port = str(proxy_port)
        if not proxy_web_port:
            self.proxy_web_port = str(conf.proxy_web_port)
        else:
            self.proxy_web_port = proxy_web_port
        if not proxy_id:
            self.proxy_id = self.reverse_proxy_url
        else:
            self.proxy_id = proxy_id
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
            "reverse_proxy_url": self.reverse_proxy_url,
            "proxy_port": self.proxy_port,
            "proxy_web_port": self.proxy_web_port,
            "proxy_id": self.proxy_id,
            "process_id": self.get_pid(),
            "proxy_settings": self.proxy_settings
        }
        return d

    def run(self):
        global current_proxy_server
        current_proxy_server = self
        server_ip = settings.config.proxy_host
        logger.warning(f'Proxy starts on http://{server_ip}:{self.proxy_port}   {Fore.CYAN}')
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
            '--mode', f'reverse:{self.reverse_proxy_url}',
            '--listen-port', self.proxy_port,
            '--web-port', self.proxy_web_port,
            '--web-host', self.proxy_ip,
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
    server = ProxyServer()
    server.start()
