from pymocker.mocker.mock_server import MockServer
import requests


class MockServerRepo:
    MockServers = {}

    @classmethod
    def add_mock_server(cls, req_data):
        reverse_mock_url = req_data.get('mock_url')
        mock_port = req_data.get('mock_port')
        mock_web_port = req_data.get('mock_web_port')
        mock_rules = req_data.get('mock_rules')
        mock_server_id = req_data.get('mock_server_id')

        if mock_server_id in cls.MockServers:
            return False, f"mock_server_id {mock_server_id} has existed"

        mock_server = MockServer(
            reverse_mock_url=reverse_mock_url,
            mock_port=mock_port,
            mock_web_port=mock_web_port,
            mock_rules=mock_rules,
            mock_server_id=mock_server_id
        )
        process = mock_server.start()
        if process.is_alive():
            cls.MockServers[mock_server.mock_server_id] = mock_server
            return True, mock_server.to_dict()
        else:
            return False, 'Process can not start'

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
            rules = req_data.get('mock_rules')
        else:
            rules = req_data
        resp = requests.put(url=f"{mock_server.get_access_url()}/mock_rules", json=rules)
        if not resp or resp.status_code != 200:
            return False, "Update remote mock server rules failed"
        mock_server.mock_rules = rules
        return True, rules

    @classmethod
    def delete_mock_server(cls, mock_server_id):
        p = cls.MockServers.get(mock_server_id)
        if p:
            p.stop()
            del cls.MockServers[mock_server_id]
            return p
        else:
            return None

