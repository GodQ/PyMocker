from pymocker.proxy.proxy_server import ProxyServer

PROXYS = {}


def add_proxy(proxy: ProxyServer):
    PROXYS[proxy.proxy_id] = proxy


def list_proxy():
    return PROXYS


def get_proxy(proxy_id):
    return PROXYS[proxy_id]


def delete_proxy(proxy_id):
    p = PROXYS[proxy_id]
    del PROXYS[proxy_id]
    return p

