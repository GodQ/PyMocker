import socket


def check_port_in_use(port, host='0.0.0.0') -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ret = s.connect_ex((host, port))
    # print(port, ret)
    s.close()
    if ret == 0:
        return True
    else:
        return False


def find_available_port(from_port: int, to_port: int, start: int = -1, host='0.0.0.0', blacklist: set = set()) -> int:
    assert to_port >= from_port
    if start == -1:
        start = from_port
    else:
        assert from_port <= start <= to_port
    size = to_port - from_port
    for i in range(0, size):
        port = i + start
        if port > to_port:
            port = port - to_port - 1 + from_port
        if check_port_in_use(port, host) is False and port not in blacklist:
            return port
    return 0


def test_find_available_port():
    start = 8081
    r = find_available_port(8080, 8089, start=start)
    print(r)
    start = r+1
    r = find_available_port(8080, 8089, start=start)
    print(r)
    start = r+1
    r = find_available_port(8080, 8089, start=start)
    print(r)


def _get_host_ip():
    s = None
    ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


HOST_IP = None


def get_host_ip():
    global HOST_IP
    if not HOST_IP:
        HOST_IP = _get_host_ip()
    return HOST_IP


# test_find_available_port()