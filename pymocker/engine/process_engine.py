"""
Base threading server class
"""

from multiprocessing import Process
from pymocker.engine.baseengine import BaseEngine, MockServer
from pymocker.mocker.starter import start


class ProcessEngine(BaseEngine):
    instances = {}

    @classmethod
    def run(cls, mock_server: MockServer, **kwargs):
        mock_server_id = mock_server.mock_server_id
        p = Process(target=start, args=(mock_server_id,), kwargs=kwargs)
        p.daemon = True
        p.start()
        cls.instances[mock_server_id] = p
        return p

    @classmethod
    def stop(cls, mock_server_id):
        mock_server = cls.instances.get(mock_server_id)
        if not mock_server:
            raise Exception('No such mock server')
        mock_server.terminate()
        mock_server.join()
        mock_server.close()

    @classmethod
    def is_alive(cls, mock_server_id):
        mock_server = cls.instances.get(mock_server_id)
        if not mock_server:
            raise Exception('No such mock server')
        return mock_server.is_alive()

    @classmethod
    def get_info(cls, mock_server_id):
        mock_server = cls.instances.get(mock_server_id)
        if not mock_server:
            raise Exception('No such mock server')
        return mock_server


