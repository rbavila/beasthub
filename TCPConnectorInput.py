from TCPConnector import TCPConnector
from BEASTParser import BEASTParser

class TCPConnectorInput(TCPConnector):
    def __init__(self, name, logger, host, port, msgqueue):
        super().__init__(name, logger, host, port)
        self.msgqueue = msgqueue
        self.parser = BEASTParser(self.msgqueue)

    def _work(self):
        msg = self._recv()
        if msg:
            self.parser.feed(msg)
