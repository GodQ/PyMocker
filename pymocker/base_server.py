"""
Base threading server class
"""

from multiprocessing import Process


class ProcessServer:

    def __init__(self):
        self.server_instance = None
        self.running = False

    def start(self, *args, **kwargs):
        if self.running:
            return
        self.running = True
        self.server_instance = Process(target=self.run, args=args, kwargs=kwargs)
        self.server_instance.start()

    def stop(self):
        self.running = False
        self.server_instance.terminate()
        self.server_instance.join()
        self.server_instance.close()

    def join(self):
        self.server_instance.join()

    def run(self):
        """
        Server main function
        """
        pass

    def is_alive(self):
        if self.server_instance:
            return self.server_instance.is_alive()
        else:
            return False


class StaticServer:

    def start(self, *args, **kwargs):
        pass

    def stop(self):
        pass