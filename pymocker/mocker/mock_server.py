
from flask import Flask, request
from pymocker.base_server import ProcessServer
from pymocker.log import get_logger
from pymocker import settings
from pymocker.proxy.proxy_server import ProxyServer


flask_app = Flask(__name__)


@flask_app.route('/proxy', methods=['POST'])
def mitm_proxy():
    req = request.json
    reverse_proxy_url = req.get('reverse_proxy_url')
    proxy_port = req.get('proxy_port')
    proxy_web_port = req.get('proxy_web_port')
    proxy_settings = req.get('proxy_settings')
    proxy_server = ProxyServer(
        reverse_proxy_url=reverse_proxy_url,
        proxy_port=proxy_port,
        proxy_web_port=proxy_web_port,
        proxy_settings=proxy_settings)
    pro = proxy_server.start()
    # proxy_server.join()
    if pro.is_alive():
        resp = proxy_server.to_dict()
        return resp, 200
    else:
        resp = {
            "error": "error"
        }
        return resp, 400


def run_mock_server():
    flask_app.run(host=settings.config.mock_host, port=settings.config.mock_port, debug=True)


if __name__ == '__main__':
    run_mock_server()
