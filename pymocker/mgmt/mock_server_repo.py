from pymocker.mocker.mock_server import MockServer


class MockServerRepo:
    MockServers = {}

    @classmethod
    def add_mock_server(cls, mock_server: MockServer):
        process = mock_server.start()
        if process.is_alive():
            cls.MockServers[mock_server.mock_server_id] = mock_server
            return True
        else:
            return False

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

