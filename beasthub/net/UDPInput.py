from UDPWorker import UDPWorker
from BEASTParser import BEASTParser

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
