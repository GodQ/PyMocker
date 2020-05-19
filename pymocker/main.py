from pymocker.mocker.mock_server import run_mock_server
from pymocker.proxy.proxy_server import proxy_server

proxy_server.start()
run_mock_server()
proxy_server.join()
