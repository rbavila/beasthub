from TCPListenerManager import TCPListenerManager
from TCPListenerOutputWorker import TCPListenerOutputWorker
from PrefixLogger import PrefixLogger

class TCPListenerOutputManager(TCPListenerManager):
    def __init__(self, name, logger, host, port, msgqueue):
        super().__init__(name, logger, host, port)
        self.msgqueue = msgqueue
        self.workers = []

    def _handle_client(self, client):
        name = "{} #{}".format(self.name, len(self.workers))
        t_logger = PrefixLogger(self.logger.logger, name)
        w = TCPListenerOutputWorker(name, t_logger, client, self.msgqueue)
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
