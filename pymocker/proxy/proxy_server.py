import socket
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


class ProxyServer(ProcessServer):

    def __init__(self, reverse_proxy_url="https://www.baidu.com"):
        super().__init__()

        conf = settings.config
        self.proxy_ip = str(conf.proxy_host)
        self.proxy_port = str(conf.proxy_port)
        self.proxy_web_port = str(conf.proxy_web_port)
        self.reverse_proxy_url = reverse_proxy_url
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

        self._master = None

    def run(self):
        server_ip = settings.config.proxy_host
        logger.warning(f'start on http://{server_ip}:{self.proxy_port}   {Fore.CYAN} ***请在被测设备上设置代理服务器地址***')
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
        mitmweb(mitm_arguments)


proxy_server = ProxyServer()


def info_msg(*msg):
    print(f'{Fore.YELLOW}[proxy_server]', *msg, Style.RESET_ALL)


if __name__ == '__main__':
    server = ProxyServer()
    server.start()
