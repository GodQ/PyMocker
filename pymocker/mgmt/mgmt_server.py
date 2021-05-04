
from flask import Flask, request
from pymocker import settings
from pymocker.mgmt.mock_server_repo import MockServerRepo
from pymocker.lib.utils import get_host_ip


flask_app = Flask(__name__)


@flask_app.route('/mock_servers', methods=['POST'])
def post_mock_servers():
    host = get_host_ip()
    if 'Host' in request.headers:
        host = request.headers['Host'].split(':')[0]
    req_data = request.json
    req_data['host'] = host
    try:
        ret, msg = MockServerRepo.add_mock_server(req_data)
    except Exception as e:
        ret = False
        msg = str(e)
    if ret:
        resp = msg
        return resp, 201
    else:
        resp = {
            "error": msg
        }
        return resp, 400


@flask_app.route('/mock_servers', methods=['GET'])
def list_mock_servers():
    show_rules = request.args.get("show_rules", 'false')
    servers = MockServerRepo.list_mock_servers()
    data = []
    for s in servers:
        ser = s.to_dict()
        if str(show_rules) != 'true':
            ser['mock_rules'] = "..."
        data.append(ser)
    resp = {
        "items": data
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


@flask_app.route('/mock_servers/<mock_server_id>', methods=['PUT'])
def put_mock_servers(mock_server_id):
    req_data = request.json
    ret, msg = MockServerRepo.put_mock_server(mock_server_id, req_data)
    if ret:
        resp = req_data
        return resp, 200
    else:
        resp = {
            "error": msg
        }
        return resp, 400


@flask_app.route('/mock_servers/<mock_server_id>', methods=['DELETE'])
def delete_mock_server(mock_server_id):
    mock_server = MockServerRepo.get_mock_server(mock_server_id)
    if mock_server:
        resp = mock_server.to_dict()
        MockServerRepo.delete_mock_server(mock_server_id)
        return resp, 204
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


def run_mgmt_server():
    flask_app.run(host=settings.config.mock_host, port=settings.config.mgmt_port, debug=True)


if __name__ == '__main__':
    run_mgmt_server()
