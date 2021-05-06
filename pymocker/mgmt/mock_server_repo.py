from pymocker.mgmt.mock_server import MockServer
from pymocker.engine.drivers import EngineDriver
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class MockServerRepo:
    MockServers = {}

    @classmethod
    def add_mock_server(cls, req_data):
        reverse_target_url = req_data.get('target_url')
        mock_port = req_data.get('mock_port')
        mock_web_port = req_data.get('mock_web_port')
        mock_rules = req_data.get('mock_rules', [])
        mock_server_id = req_data.get('mock_server_id')
        host = req_data.get('host')

        if mock_server_id in cls.MockServers:
            return False, f"mock_server_id {mock_server_id} has existed"

        try:
            if isinstance(mock_rules, bytes):
                mock_rules = mock_rules.decode()
            if isinstance(mock_rules, str):
                mock_rules = json.loads(mock_rules)
        except Exception as e:
            return False, f'Error: format of mock_rules is not list, {str(e)}'

        mock_server = MockServer(
            reverse_target_url=reverse_target_url,
            mock_port=mock_port,
            mock_web_port=mock_web_port,
            mock_rules=mock_rules,
            mock_server_id=mock_server_id,
            host=host
        )
        ins = EngineDriver.get_engine().run(mock_server)
        print('Mock server created', ins)
        if ins.is_alive():
            cls.MockServers[mock_server.mock_server_id] = mock_server
            return True, mock_server.to_dict()
        else:
            return False, 'Mock server can not start'

    @classmethod
    def list_mock_servers(cls):
        return cls.MockServers.values()

    @classmethod
    def get_mock_server(cls, mock_server_id):
        return cls.MockServers.get(mock_server_id)

    @classmethod
    def put_mock_server(cls, mock_server_id, req_data):
        mock_server: MockServer = cls.MockServers.get(mock_server_id)
        if not mock_server:
            return False, "Not Found"
        if isinstance(req_data, dict):
            rules = req_data.get('mock_rules', [])
        else:
            rules = req_data
        try:
            if isinstance(rules, bytes):
                rules = rules.decode()
            if isinstance(rules, str):
                rules = json.loads(rules)
        except Exception as e:
            return False, f'Error: format of mock_rules is not list, {str(e)}'

        resp = requests.put(url=f"{mock_server.get_access_url()}/mock_rules", json=rules, verify=False)
        if not resp or resp.status_code != 200:
            return False, "Update remote mock server rules failed"
        mock_server.mock_rules = rules
        return True, rules

    @classmethod
    def delete_mock_server(cls, mock_server_id):
        p = cls.MockServers.get(mock_server_id)
        if p:
            EngineDriver.get_engine().stop(mock_server_id)
            print('Mock server deleted', mock_server_id)
            del cls.MockServers[mock_server_id]
            return p
        else:
            return None

