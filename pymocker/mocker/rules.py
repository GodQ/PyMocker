from mitmproxy import http
import re
import json
import jsonpath


class Request:
    def __init__(self, **kwargs):
        self.method = kwargs.get('method')
        self.path = kwargs.get('path')
        self.params = kwargs.get('params')
        self.headers = kwargs.get('headers')
        self.data = kwargs.get('data')
        self.urlencoded_form = kwargs.get('urlencoded_form')

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
        self.data = kwargs.get('data', "")
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
    from pymocker.mocker.mock_server import current_mock_server
    mock_rules = current_mock_server.mock_rules
    return mock_rules


def set_mock_rules(rules: list):
    from pymocker.mocker.mock_server import current_mock_server
    current_mock_server.mock_rules = rules


def process_request(req: Request) -> Response:
    current_mock_rules = get_mock_rules()
    resp = Response()
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
    for rule in current_mock_rules:
        ret = process_one_rule(rule, req, resp)
        if ret is True:
            return resp
    return None


def process_one_rule(rule: dict, req: Request, resp: Response) -> bool:
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

    # Pass all validate
    resp.status = rule.get('response_status', 200)
    resp.headers = rule.get('response_headers', {})
    resp.data = rule.get('response_data', "")
    if isinstance(resp.data, dict):
        resp.data = json.dumps(resp.data)
        resp.headers['Content-Type'] = "application/json"
    return True

