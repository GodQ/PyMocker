import enum
import json
from pathlib import Path
from colorama import Fore, Style
from pymocker.mgmt.port_repo import PortRepo
from pymocker.lib.log import get_logger
from pymocker.lib.utils import get_host_ip
from pymocker.app_init import db

"""
HTTP proxy server
"""

CURRENT_PATH = Path(__file__).parent
logger = get_logger()


class MockServerRecord(db.Model):
    mock_server_id = db.Column(db.String(80), primary_key=True)
    target_url = db.Column(db.String(80))
    mock_rules = db.Column(db.JSON)

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d)

    def to_dict(self):
        d = {
            "target_url": self.target_url,
            "mock_server_id": self.mock_server_id,
            "mock_rules": self.mock_rules,
            "mock_port": '',
            "mock_web_port": '',
            "access_url": '',
            "monitor_web_url": ''
        }
        return d


class ServerStatus:
    RUNNING = 'running'
    STOPPED = 'stopped'


class MockServerInstance:

    def __init__(self, mocker_server: MockServerRecord):
        self.mock_server_id = mocker_server.mock_server_id
        self.target_url = mocker_server.target_url
        self.mock_rules = mocker_server.mock_rules

        self.mock_web_port = None
        self.mock_port = None
        self.host = None
        self.url_schema = None
        self.running_status = ServerStatus.STOPPED
        self.prepare()

    def status(self):
        return self.running_status

    def is_running(self):
        return self.running_status == ServerStatus.RUNNING

    def set_running(self):
        self.set_status(ServerStatus.RUNNING)

    def set_stopped(self):
        self.set_status(ServerStatus.STOPPED)

    def set_status(self, status):
        self.running_status = status

    def update_mock_rules(self, mock_rules):
        record = MockServerRecord.query.filter_by(mock_server_id=self.mock_server_id).first()
        if not record:
            return False, f"No mock_server_id {self.mock_server_id} found"
        record.mock_rules = mock_rules
        db.session.commit()
        self.mock_rules = mock_rules

    def prepare(self):
        self.url_schema = self.get_url_schema()
        self.host = get_host_ip()

        # if mock_port:
        #     mock_port = int(mock_port)
        #     port_available = PortRepo.check_port_available(mock_port)
        #     if port_available is False:
        #         raise Exception(f"The mock_port {mock_port} is in use")
        #     self.mock_port = mock_port
        # elif not self.mock_port:
        self.mock_port = PortRepo.find_available_port()

        # if mock_web_port:
        #     mock_web_port = int(mock_web_port)
        #     port_available = PortRepo.check_port_available(mock_web_port)
        #     if port_available is False:
        #         raise Exception(f"The mock_web_port {mock_web_port} is in use")
        #     self.mock_web_port = mock_web_port
        # elif not self.mock_web_port:
        self.mock_web_port = PortRepo.find_available_port()

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

    def release(self):
        PortRepo.release_port(self.mock_port)
        PortRepo.release_port(self.mock_web_port)

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d)

    def to_dict(self):
        d = {
            "target_url": self.target_url,
            "mock_port": self.mock_port,
            "mock_web_port": self.mock_web_port,
            "mock_server_id": self.mock_server_id,
            # "process_id": self.get_pid(),
            "mock_rules": self.mock_rules,
            "access_url": self.get_access_url(),
            "monitor_web_url": self.get_monitor_url(),
            "status": self.running_status
        }
        return d

    def get_access_url(self):
        return f"{self.url_schema}://{self.host}:{self.mock_port}"

    def get_monitor_url(self):
        return f"http://{self.host}:{self.mock_web_port}"

    def get_url_schema(self):
        if self.target_url.split(':')[0] == 'https':
            self.url_schema = 'https'
        else:
            self.url_schema = 'http'
        return self.url_schema


def info_msg(*msg):
    print(f'{Fore.YELLOW}[proxy_server]', *msg, Style.RESET_ALL)


if __name__ == '__main__':
    record = MockServerRecord(mock_server_id='0001', target_url='https://www.baidu.com')
    server = MockServerInstance(record)
    print(server.to_dict())

    # db.create_all()
