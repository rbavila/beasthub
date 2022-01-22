from TCPListenerWorker import TCPListenerWorker
from BEASTParser import BEASTParser

class TCPListenerInputWorker(TCPListenerWorker):
    def __init__(self, name, logger, socket, msgqueue):
        super().__init__(name, logger, socket)
        self.msgqueue = msgqueue
        self.parser = BEASTParser(self.msgqueue)

    def _work(self):
        msg = self._recv()
        if msg:
            self.parser.feed(msg)
