from pymocker.mocker.mock_server import MockServer


class MockServerRepo:
    MockServers = {}

    @classmethod
    def add_mock_server(cls, req):
        reverse_mock_url = req.get('mock_url')
        mock_port = req.get('mock_port')
        mock_web_port = req.get('mock_web_port')
        mock_rules = req.get('mock_rules')
        mock_server_id = req.get('mock_server_id')

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
    def delete_mock_server(cls, mock_server_id):
        p = cls.MockServers.get(mock_server_id)
        if p:
            p.stop()
            del cls.MockServers[mock_server_id]
            return p
        else:
            return None

