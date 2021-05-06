from pymocker.mgmt.mock_server import MockServer


class BaseEngine:
    instances = None

    @classmethod
    def run(cls, mock_server: MockServer):
        pass

    @classmethod
    def stop(cls, mock_server_id):
        pass

    @classmethod
    def is_alive(cls, mock_server_id):
        pass

    @classmethod
    def get_info(cls, mock_server_id):
        pass
