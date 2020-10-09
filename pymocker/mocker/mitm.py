from mitmproxy import http
from pymocker.lib.log import get_logger
from pymocker.mocker.rules import process_request
from pymocker.mocker.rules import Request

"""
Script for mitmdump
Redirect request from proxy server to real server
"""

_logger = get_logger()


def request(flow: http.HTTPFlow) -> None:
    # pretty_url takes the "Host" header of the request into account, which
    # is useful in transparent mode where we usually only have the IP otherwise.

    path = flow.request.path.split('?')[0]
    method = flow.request.method
    params = flow.request.query
    headers = flow.request.headers
    data = flow.request.content
    req = Request(method=method, path=path, params=params, headers=headers, data=data)
    print(req)
    resp = process_request(req)
    if resp and not resp.empty():
        flow.response = http.HTTPResponse.make(
            resp.status,  # (optional) status code
            resp.data,  # (optional) content
            resp.headers  # (optional) headers
        )
