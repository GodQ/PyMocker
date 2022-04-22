"""
Base threading server class
"""

from multiprocessing import Process
from pymocker.engine.baseengine import BaseEngine, MockServerInstance
from pymocker.mocker.starter import start as start_mock_server


class ProcessEngine(BaseEngine):
    instances = {}

    @classmethod
    def run(cls, mock_server: MockServerInstance, **kwargs):
        mock_server_id = mock_server.mock_server_id
        if mock_server_id in cls.instances:
            return cls.instances[mock_server_id].is_alive()
        p = Process(target=start_mock_server, args=(mock_server_id,), kwargs=kwargs)
        p.daemon = True
        p.start()
        cls.instances[mock_server_id] = p
        print(p)
        return p.is_alive()

    @classmethod
    def stop(cls, mock_server_id):
        mock_server_process = cls.instances.get(mock_server_id)
        if not mock_server_process:
            raise Exception('No such mock server')
        mock_server_process.terminate()
        mock_server_process.join()
        # mock_server_process.close()
        del cls.instances[mock_server_id]

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


