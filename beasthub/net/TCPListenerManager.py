import socket
import random
import time
from Worker import Worker

class TCPListenerManager(Worker):
    def __init__(self, name, logger, host, port):
        super().__init__(name, logger)
        self.hostport = (host, port)
        self.socket = socket.socket()
        self.socket.bind(self.hostport)
        self.socket.listen()
        self.socket.settimeout(5)

    def _work(self):
        try:
            (client_socket, client_addr) = self.socket.accept()
            client_socket.settimeout(5)
            self._handle_client(client_socket)
        except socket.timeout:
            return

    def _handle_client(self, client):
        pass
