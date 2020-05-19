
from flask import Flask
from pymocker.base_server import ProcessServer
from pymocker.log import get_logger
from pymocker import settings
from pymocker.proxy.proxy_server import ProxyServer


flask_app = Flask(__name__)


@flask_app.route('/path')
def hello_world():
    return 'Hello, Mocker!!!  Welcome!!'


def run_mock_server():
    flask_app.run(host=settings.config.mock_host, port=settings.config.mock_port)


if __name__ == '__main__':
    run_mock_server()
