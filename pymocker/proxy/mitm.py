from mitmproxy import http
from pymocker import settings
from pymocker import log

"""
Script for mitmdump
Redirect request from proxy server to mock server
"""

_logger = log.get_logger()


def to_mock_server(flow: http.HTTPFlow):
    conf = settings.config
    # mock path 为/mock开头加上原始url
    # flow.request.path = '/mock/' + flow.request.url
    # mock scheme 统一为http
    flow.request.scheme = 'http'
    # mock server port
    flow.request.port = conf.mock_port
    # mock server ip
    flow.request.host = conf.mock_host
    # device real ip
    address = flow.client_conn.address[0]
    # 获取的address是IPv6（内嵌IPv4地址表示法），需要获取IPv4地址，需要做以下处理
    if address.startswith('::ffff:'):
        address = address.split('::ffff:')[1]
    flow.request.headers['PyMocker-Client-Address'] = address
    _logger.info('Redirect-> %s' % flow.request.url[:100])


def request1(flow: http.HTTPFlow):
    conf = settings.config
    _logger.info(flow.request.url[:100])
    filters = conf.get('proxy.filters')
    if not filters:
        to_mock_server(flow)
        return
    for _filter in filters:
        if _filter in flow.request.host:
            to_mock_server(flow)
            break


def request(flow: http.HTTPFlow) -> None:
    # pretty_url takes the "Host" header of the request into account, which
    # is useful in transparent mode where we usually only have the IP otherwise.

    print(flow.request.pretty_url, flow.request.path)
    # print(dir(flow.request))
    if flow.request.path == "/path":
        # flow.response = http.HTTPResponse.make(
        #     200,  # (optional) status code
        #     b"Hello World",  # (optional) content
        #     {"Content-Type": "text/html"}  # (optional) headers
        # )
        to_mock_server(flow)


# def responseheaders(flow):
#     """
#     Enables streaming for all responses.
#     This is equivalent to passing `--set stream_large_bodies=1` to mitmproxy.
#     """
#     flow.response.stream = True