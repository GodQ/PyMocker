import re
import json
import jsonpath
import copy
import requests
import os
from pymocker.config import config


built_in_apis = ['/mock_rules', '/mock_records']


def is_build_in_api(req_url):
    for api in built_in_apis:
        if api in req_url:
            return True
    return False


class MockInfo:
    def __init__(self):
        self.mock_server_id = ''
        self.target_url = ''
        self.mock_rules = []
        self.mock_port = None
        self.mock_web_port = None

    def load(self, config):
        self.mock_server_id = config.get('mock_server_id')
        self.target_url = config.get('target_url')
        self.mock_rules = config.get('mock_rules', [])
        self.mock_port = config.get('mock_port', None)
        self.mock_web_port = config.get('mock_web_port', None)


current_mock_server = MockInfo()


class Request:
    def __init__(self, **kwargs):
        self.method = kwargs.get('method')
        self.path = kwargs.get('path')
        self.params = kwargs.get('params')
        self.headers = kwargs.get('headers')
        self.data = kwargs.get('data')
        self.urlencoded_form = kwargs.get('urlencoded_form')

        if isinstance(self.data, bytes):
            self.data = self.data.decode()
        if isinstance(self.data, str):
            try:
                self.data = json.loads(self.data)
            except Exception as e:
                pass

    def __str__(self):
        desc = [f"Content of Request <{self.__hash__()}>:"]
        for field in self.__dict__:
            desc.append(f"    {field}: {self.__dict__[field]}")
        desc = "\n".join(desc)
        return desc


class Response:
    def __init__(self, **kwargs):
        self.status = kwargs.get('status')
        self.headers = kwargs.get('headers', {})
        self.data = kwargs.get('data', {})
        self.urlencoded_form = kwargs.get('urlencoded_form', {})

    def empty(self):
        if not self.status:
            return True
        else:
            return False

    def __str__(self):
        desc = [f"Content of Response <{self.__hash__()}>:"]
        for field in self.__dict__:
            desc.append(f"    {field}: {self.__dict__[field]}")
        desc = "\n".join(desc)
        return desc


def get_mock_rules():
    mock_rules = current_mock_server.mock_rules
    return mock_rules


def set_mock_rules(rules: list):
    current_mock_server.mock_rules = rules


def refresh_settings_from_remote(mock_server_id=None):
    if not mock_server_id:
        mock_server_id = os.environ.get('mock_server_id', None)
    assert mock_server_id
    mgmt_url = f'http://{config.mgmt_host}:{config.mgmt_port}/mock_servers/{mock_server_id}'
    resp = requests.get(mgmt_url)
    print("Fetch mock server config from mgmt, status: ", mock_server_id, resp.status_code, resp.reason)
    assert resp.status_code == 200, f'{mgmt_url}, {resp.status_code}, {resp.reason}, {resp.content}'
    settings = resp.json()
    # print(mgmt_url)
    # print(settings)
    current_mock_server.load(settings)
    return settings


def process_request(req: Request) -> Response:
    current_mock_rules = get_mock_rules()
    resp = Response()
    # mock server built-in api
    if req.path == '/mock_rules':
        if req.method.lower() == 'get':
            resp.status = 200
            resp.data = json.dumps(get_mock_rules())
            resp.headers = {"Content-Type": "application/json"}
            return resp
        elif req.method.lower() == 'put':
            rules = req.data
            if isinstance(rules, bytes):
                rules = rules.decode()
            if isinstance(rules, str):
                rules = json.loads(rules)
            if isinstance(rules, dict):
                rules = rules.get('mock_rules')
            if not isinstance(rules, list):
                resp.status = 400
                resp.data = json.dumps(
                    {"error": f'Mock rules format error, only list supported, but is {type(rules)}'}
                )
                resp.headers = {"Content-Type": "application/json"}
                return resp
            # elif not rules:
            #     resp.status = 400
            #     resp.data = json.dumps({"error": 'No mock rules'})
            #     resp.headers = {"Content-Type": "application/json"}
            #     return resp
            else:
                set_mock_rules(rules)
                resp.status = 200
                resp.data = json.dumps(get_mock_rules())
                resp.headers = {"Content-Type": "application/json"}
                return resp
    elif req.path == '/refresh':
        refresh_settings_from_remote()
        resp.status = 200
        resp.data = {'msg': 'refreshed'}
        resp.headers = {"Content-Type": "application/json"}
        return resp

    elif req.path == '/mock_records':
        if req.method.lower() == 'get':
            from pymocker.mocker.stats import HttpRecordStore
            resp.status = 200
            resp.data = json.dumps(HttpRecordStore.get_http_records())
            resp.headers = {"Content-Type": "application/json"}
            return resp

    # Traverse rules list to match every rule
    rule = match_any_rule(req)
    if rule:
        resp = process_by_rule(rule, req, resp)
        return resp
    return None


def exec_python_script(python_script: str, rule: dict, request: Request, response: Response):
    vars = {
        'rule': rule,
        'request': request,
        'response': response
    }
    # exec(object=python_script, __locals=vars, __globals=vars)
    exec(python_script)


def match_any_rule(req: Request) -> dict:
    for rule in get_mock_rules():
        if match_one_rule(rule, req) is True:
            return rule
    return None


def match_one_rule(rule: dict, req: Request) -> bool:
    rule_method = rule.get('method', "")
    if rule_method:
        if rule_method.lower() != req.method.lower():
            return False
    rule_path = rule.get('path')
    if rule_path:
        if not re.match(rule_path, req.path):
            return False
    rule_params = rule.get('params')
    if rule_params:
        for k, v in rule_params.items():
            if k not in req.params:
                return False
            if req.params[k] != v:
                return False

    rule_headers = rule.get('headers')
    if rule_headers:
        for k, v in rule_headers.items():
            if k not in req.headers:
                return False
            if req.headers[k] != v:
                return False

    rule_data = rule.get('data')
    if rule_data:
        for k, v in rule_data.items():
            val = jsonpath.jsonpath(req.data, k)
            if val is False or val[0] != v:
                return False
    return True


def process_by_rule(rule: dict, req: Request, resp: Response) -> Response:
    # Pass all validate
    resp.status = rule.get('response_status', 200)
    resp.headers = rule.get('response_headers', {})
    resp.data = rule.get('response_data', {})
    python_script = rule.get('python_script')
    if python_script:
        exec_python_script(python_script, rule=copy.deepcopy(rule), request=req, response=resp)
    if isinstance(resp.data, dict):
        resp.data = json.dumps(resp.data)
        resp.headers['Content-Type'] = "application/json"
    return resp

