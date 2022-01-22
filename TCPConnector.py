import socket
import random
import time
from Worker import Worker

class TCPConnector(Worker):
    def __init__(self, name, logger, host, port):
        super().__init__(name, logger)
        self.hostport = (host, port)
        self.socket = None

    def _connect(self):
        self.logger.log("Connecting to {}".format(self.hostport))
        self.socket = None
        while not self.socket and not self.done:
            try:
                self.socket = socket.create_connection(self.hostport)
                self.socket.settimeout(5)
                self.logger.log("Successfully connected to {}".format(self.hostport))
            except OSError as e:
                self.logger.log("Connection failed: {}".format(e))
                t = random.randint(2, 10)
                self.logger.log("Retrying in {} seconds...".format(t))
                time.sleep(t)
                self.socket = None

    def _pre_work(self):
        super()._pre_work()
        self._connect()

    def _recv(self):
        try:
            msg = self.socket.recv(1024)
        except socket.timeout:
            return None
        self.logger.debug("Received {}".format(msg.hex()))
        if not msg:
            self.logger.log("Lost connection to {}, trying to reconnect".format(self.hostport))
            self._connect()
            return None
        else:
            return msg

    def _send(self, msg):
        sent = False
        while not sent and not self.done:
            try:
                self.socket.sendall(msg)
                sent = True
            except ConnectionError:
                self.logger.log("Lost connection to {}, trying to reconnect".format(self.hostport))
                self._connect()
