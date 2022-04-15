import traceback
from flask import request
from pymocker import config
from pymocker.mgmt.mock_server_mgmt import MockServerMgmt
from pymocker.app_init import app as flask_app


@flask_app.route('/mock_servers', methods=['POST'])
def post_mock_servers():
    req_data = request.json
    if 'target_url' not in req_data:
        resp = {
            'error': 'target_url must specify'
        }
        return resp, 400
    if 'mock_server_id' not in req_data:
        resp = {
            'error': 'mock_server_id must specify'
        }
        return resp, 400

    try:
        ret, msg = MockServerMgmt.add_mock_server(req_data)
    except Exception as e:
        tb = traceback.format_exc()
        ret = False
        msg = str(e) + '\n' + tb
        print(msg)
    if ret is True:
        resp = {'info': 'created'}
        return resp, 201
    else:
        resp = {
            "error": msg
        }
        return resp, 400


@flask_app.route('/mock_servers', methods=['GET'])
def list_mock_servers():
    show_rules = request.args.get("show_rules", 'false')
    servers = MockServerMgmt.list_mock_servers()
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
    mock_server = MockServerMgmt.get_mock_server(mock_server_id)
    if mock_server:
        resp = mock_server.to_dict()
        return resp, 200
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


@flask_app.route('/mock_servers/<mock_server_id>/mock_rules', methods=['GET'])
def get_mock_server_mock_rules(mock_server_id):
    mock_server = MockServerMgmt.get_mock_server(mock_server_id)
    if mock_server:
        resp = {
            "mock_rules": mock_server.mock_rules
        }
        return resp, 200
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


@flask_app.route('/mock_servers/<mock_server_id>', methods=['PUT'])
def put_mock_servers(mock_server_id):
    req_data = request.json
    ret, msg = MockServerMgmt.put_mock_server(mock_server_id, req_data)
    if ret:
        resp = req_data
        return resp, 200
    else:
        resp = {
            "error": msg
        }
        return resp, 400


@flask_app.route('/mock_servers/<mock_server_id>/start', methods=['POST'])
def start_mock_server(mock_server_id):
    mock_server = MockServerMgmt.get_mock_server(mock_server_id)
    if mock_server:
        resp = mock_server.to_dict()
        MockServerMgmt.start_mock_server(mock_server_id)
        return resp, 201
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


@flask_app.route('/mock_servers/<mock_server_id>/start', methods=['DELETE'])
def stop_mock_server(mock_server_id):
    mock_server = MockServerMgmt.get_mock_server(mock_server_id)
    if mock_server:
        # resp = mock_server.to_dict()
        MockServerMgmt.stop_mock_server(mock_server_id)
        return {}, 204
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


@flask_app.route('/mock_servers/<mock_server_id>', methods=['DELETE'])
def delete_mock_server(mock_server_id):
    mock_server = MockServerMgmt.get_mock_server(mock_server_id)
    if mock_server:
        resp = mock_server.to_dict()
        MockServerMgmt.delete_mock_server(mock_server_id)
        return resp, 200
    else:
        resp = {
            "error": "Not Found"
        }
        return resp, 404


def run_mgmt_server():
    flask_app.run(host='0.0.0.0', port=config.config.mgmt_port, debug=True)


if __name__ == '__main__':
    run_mgmt_server()
