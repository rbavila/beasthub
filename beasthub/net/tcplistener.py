import socket
import random
import time
import queue

from beasthub.worker import Worker
from beasthub.beast import BEASTParser

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


class TCPListenerInputManager(TCPListenerManager):
    def __init__(self, name, logger, host, port, msgqueue):
        super().__init__(name, logger, host, port)
        self.msgqueue = msgqueue
        self.workers = []

    def _handle_client(self, client):
        name = "{} client #{}".format(self.name, len(self.workers))
        w = TCPListenerInputWorker(name, self.logger, client, self.msgqueue)
        self.workers.append(w)
        w.start()

    def _post_work(self):
        for w in self.workers:
            w.shutdown()
        for w in self.workers:
            w.join()
        super()._post_work()


class TCPListenerOutputManager(TCPListenerManager):
    def __init__(self, name, logger, host, port, msgqueue):
        super().__init__(name, logger, host, port)
        self.msgqueue = msgqueue
        self.workers = []

    def _handle_client(self, client):
        name = "{} client #{}".format(self.name, len(self.workers))
        w = TCPListenerOutputWorker(name, self.logger, client, self.msgqueue)
        self.workers.append(w)
        w.start()

    def _post_work(self):
        for w in self.workers:
            w.shutdown()
        for w in self.workers:
            w.join()
        super()._post_work()

    def handle(self, msg):
        for w in self.workers:
            if not w.done:
                w.msgqueue.put(msg)


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
            self.log("Connection lost, shutting down")
            self.done = True
            return None
        else:
            return msg

    def _send(self, msg):
        try:
            self.socket.sendall(msg)
        except ConnectionError:
            self.log("Connection lost, shutting down")
            self.done = True


class TCPListenerInputWorker(TCPListenerWorker):
    def __init__(self, name, logger, socket, msgqueue):
        super().__init__(name, logger, socket)
        self.msgqueue = msgqueue
        self.parser = BEASTParser(self.msgqueue)

    def _work(self):
        msg = self._recv()
        if msg:
            self.parser.feed(msg)


class TCPListenerOutputWorker(TCPListenerWorker):
    def __init__(self, name, logger, socket, msgqueue):
        super().__init__(name, logger, socket)
        self.msgqueue = msgqueue

    def _work(self):
        try:
            msg = self.msgqueue.get(timeout=5)
            self._send(msg)
        except queue.Empty:
            return
