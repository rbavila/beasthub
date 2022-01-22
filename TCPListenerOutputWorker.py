import queue
from TCPListenerWorker import TCPListenerWorker

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
