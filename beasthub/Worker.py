from threading import Thread

class Worker(Thread):
    def __init__(self, name, logger):
        super().__init__(name=name, daemon=True)
        self.logger = logger
        self.done = False

    def shutdown(self):
        self.done = True

    def run(self):
        self._pre_work()
        while not self.done:
            self._work()
        self._post_work()

    def _pre_work(self):
        self.log("Starting")

    def _work(self):
        pass

    def _post_work(self):
        self.log("Done")

    def log(self, msg):
        self.logger.log("[{}] {}".format(self.name, msg))

    def debug(self, msg):
        self.logger.debug("[{}] {}".format(self.name, msg))
