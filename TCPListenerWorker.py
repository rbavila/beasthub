import socket
import random
import time
from Worker import Worker

class TCPListenerWorker(Worker):
    def __init__(self, name, logger, socket):
        super().__init__(name, logger)
        self.socket = socket

    def _recv(self):
        try:
            msg = self.socket.recv(1024)
        except socket.timeout:
            return None
        self.logger.debug("Received {}".format(msg.hex()))
        if not msg:
            self.logger.log("Connection lost, shutting down")
            self.done = True
            return None
        else:
            return msg

    def _send(self, msg):
        try:
            self.socket.sendall(msg)
        except ConnectionError:
            self.logger.log("Connection lost, shutting down")
            self.done = True
