
from flask import Flask, request
from pymocker.base_server import ProcessServer
from pymocker.log import get_logger
from pymocker import settings
from pymocker.mocker.mock_server import MockServer
from pymocker.mgmt.mock_server_repo import MockServerRepo


flask_app = Flask(__name__)


@flask_app.route('/mock_servers', methods=['POST'])
def post_mock_servers():
    req = request.json
    reverse_mock_url = req.get('mock_url')
    mock_port = req.get('mock_port')
    mock_web_port = req.get('mock_web_port')
    mock_rules = req.get('mock_rules')
    mock_server_id = req.get('mock_server_id')
    mock_server = MockServer(
        reverse_mock_url=reverse_mock_url,
        mock_port=mock_port,
        mock_web_port=mock_web_port,
        mock_rules=mock_rules,
        mock_server_id=mock_server_id
    )
    ret = MockServerRepo.add_mock_server(mock_server)
    if ret:
        resp = mock_server.to_dict()
        return resp, 200
    else:
        resp = {
            "error": "Create Error"
        }
        return resp, 400


@flask_app.route('/mock_servers', methods=['GET'])
def list_mock_servers():
    servers = MockServerRepo.list_mock_servers()
    data = []
    for s in servers:
        data.append(s.to_dict())
    resp = {
        "mock_servers": data
    }
    return resp, 200


@flask_app.route('/mock_servers/<mock_server_id>', methods=['GET'])
def get_mock_server(mock_server_id):
    mock_server = MockServerRepo.get_mock_server(mock_server_id)
    if mock_server:
        resp = mock_server.to_dict()
        return resp, 200
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


@flask_app.route('/mock_servers/<mock_server_id>', methods=['DELETE'])
def delete_mock_server(mock_server_id):
    mock_server = MockServerRepo.get_mock_server(mock_server_id)
    if mock_server:
        MockServerRepo.delete_mock_server(mock_server_id)
        resp = mock_server.to_dict()
        return resp, 200
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404



def run_mgmt_server():
    flask_app.run(host=settings.config.mock_host, port=settings.config.mock_port, debug=True)


if __name__ == '__main__':
    run_mgmt_server()
