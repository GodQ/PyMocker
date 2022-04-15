from pymocker.lib.utils import find_available_port, check_port_in_use


class PortRepo:
    from_port = 8000
    to_port = 9000
    start = 8000
    used_ports = set()

    @classmethod
    def find_available_port(cls):
        port = find_available_port(cls.from_port, cls.to_port, cls.start, blacklist=cls.used_ports)
        if not port:
            return None
        cls.start += 1
        if cls.start == cls.to_port + 1:
            cls.start = cls.from_port
        cls.used_ports.add(port)
        return port

    @classmethod
    def check_port_available(cls, port: int):
        return not check_port_in_use(port)

    @classmethod
    def release_port(cls, port: int):
        cls.used_ports.remove(port)

