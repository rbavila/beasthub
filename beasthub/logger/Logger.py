from threading import Lock

class Logger:
    LOG_QUIET = 0
    LOG_INFO = 1
    LOG_DEBUG = 2

    def __init__(self, loglevel):
        if self.LOG_QUIET <= loglevel <= self.LOG_DEBUG:
            self.loglevel = loglevel
        else:
            raise Exception("Invalid log level '{}'".format(loglevel))
        self.mutex = Lock()

    def log(self, msg):
        if self.loglevel >= self.LOG_INFO:
            self.mutex.acquire()
            self._log(msg)
            self.mutex.release()

    def debug(self, msg):
        if self.loglevel >= self.LOG_DEBUG:
            self.mutex.acquire()
            self._debug(msg)
            self.mutex.release()

    def _log(self, msg):
        print(msg, flush=True)

    def _debug(self, msg):
        print("DEBUG: {}".format(msg), flush=True)
