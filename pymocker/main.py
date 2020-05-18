from pymocker.proxy.proxy_server import ProxyServer
from pymocker.mocker.mock_server import MockServer


proxy_server = ProxyServer()
mock_server = MockServer()
proxy_server.start()
mock_server.start()