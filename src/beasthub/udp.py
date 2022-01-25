import socket
import random
import time
import queue

from beasthub.worker import Worker
from beasthub.beast import BEASTParser

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
                self.log("Error sending message: {}".format(e))
                t = random.randint(2, 10)
                self.log("Retrying in {} seconds...".format(t))
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


class UDPInput(UDPWorker):
    def __init__(self, name, logger, host, port, msgqueue):
        super().__init__(name, logger, host, port)
        self.msgqueue = msgqueue
        self.parser = BEASTParser(self.msgqueue)

    def _pre_work(self):
        super()._pre_work()
        self._bind()

    def _work(self):
        msg = self._recv()
        if msg:
            self.parser.feed(msg)


class UDPOutput(UDPWorker):
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
