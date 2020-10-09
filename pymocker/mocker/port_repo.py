from pymocker.lib.utils import find_available_port, check_port_in_use


class PortRepo:
    from_port = 8000
    to_port = 9000
    start = 8000

    @classmethod
    def find_available_port(cls):
        port = find_available_port(cls.from_port, cls.to_port, cls.start)
        if not port:
            return None
        cls.start += 1
        if cls.start == cls.to_port + 1:
            cls.start = cls.from_port
        return port

    @classmethod
    def check_port_available(cls, port: int):
        return not check_port_in_use(port)

