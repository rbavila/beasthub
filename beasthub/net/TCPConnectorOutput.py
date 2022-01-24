import queue
from TCPConnector import TCPConnector

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
