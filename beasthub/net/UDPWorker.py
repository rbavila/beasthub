import socket
import random
import time
from Worker import Worker

class UDPWorker(Worker):
    def __init__(self, name, logger, host, port):
        super().__init__(name, logger)
        self.hostport = (host, port)
        self.socket = socket.socket(type=socket.SOCK_DGRAM)

    def _send(self, msg):
        bytes_sent = 0
        while bytes_sent == 0 and not self.done:
            try:
                bytes_sent = self.socket.sendto(msg, self.hostport)
            except socket.gaierror as e:
                self.logger.log("Error sending message: {}".format(e))
                t = random.randint(2, 10)
                self.logger.log("Retrying in {} seconds...".format(t))
                time.sleep(t)

    def _bind(self):
        self.socket.bind(self.hostport)
        self.socket.settimeout(5)

    def _recv(self):
        try:
            msg = self.socket.recv(1024)
            return msg
        except socket.timeout:
            return None
