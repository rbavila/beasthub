import socket
import random
import time
import queue

from beasthub.worker import Worker
from beasthub.beast import BEASTParser

class TCPConnector(Worker):
    def __init__(self, name, logger, host, port):
        super().__init__(name, logger)
        self.hostport = (host, port)
        self.socket = None

    def _connect(self):
        self.log("Connecting to {}".format(self.hostport))
        self.socket = None
        while not self.socket and not self.done:
            try:
                self.socket = socket.create_connection(self.hostport)
                self.socket.settimeout(5)
                self.log("Successfully connected to {}".format(self.hostport))
            except OSError as e:
                self.log("Connection failed: {}".format(e))
                t = random.randint(2, 10)
                self.log("Retrying in {} seconds...".format(t))
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
            self.log("Lost connection to {}, trying to reconnect".format(self.hostport))
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
                self.log("Lost connection to {}, trying to reconnect".format(self.hostport))
                self._connect()


class TCPConnectorInput(TCPConnector):
    def __init__(self, name, logger, host, port, msgqueue):
        super().__init__(name, logger, host, port)
        self.msgqueue = msgqueue
        self.parser = BEASTParser(self.msgqueue)

    def _work(self):
        msg = self._recv()
        if msg:
            self.parser.feed(msg)


class TCPConnectorOutput(TCPConnector):
    def __init__(self, name, logger, host, port):
        super().__init__(name, logger, host, port)
        self.msgqueue = queue.SimpleQueue()

    def _work(self):
        try:
            msg = self.msgqueue.get(timeout=5)
            self._send(msg)
        except queue.Empty:
            return

    def handle(self, msg):
        self.msgqueue.put(msg)
