import queue
from Worker import Worker

class Dispatcher(Worker):
    def __init__(self, name, logger, msgqueue, output_workers):
        super().__init__(name, logger)
        self.msgqueue = msgqueue
        self.output_workers = output_workers

    def _work(self):
        try:
            msg = self.msgqueue.get(timeout=5)
            for t in self.output_workers:
                t.handle(msg)
        except queue.Empty:
            return
