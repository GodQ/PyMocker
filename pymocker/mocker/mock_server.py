
from flask import Flask
from pymocker.base_server import ProcessServer
from pymocker.log import get_logger
from pymocker import settings


flask_app = Flask(__name__)


@flask_app.route('/path')
def hello_world():
    return 'Hello, World! Mocker Welcome!!'


class MockServer(ProcessServer):

    def __init__(self, app=flask_app):
        super().__init__()
        self.app = app

    def run(self):
        self.app.run(host=settings.config.mock_host, port=settings.config.mock_port)
        print('OK')


if __name__ == '__main__':
    mocker = MockServer()
    mocker.start()
