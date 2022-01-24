import threading
import syslog

LOG_QUIET = 0
LOG_INFO = 1
LOG_DEBUG = 2

class Logger:
    def __init__(self, loglevel):
        if LOG_QUIET <= loglevel <= LOG_DEBUG:
            self.loglevel = loglevel
        else:
            raise Exception("Invalid log level '{}'".format(loglevel))
        self.mutex = threading.Lock()

    def log(self, msg):
        if self.loglevel >= LOG_INFO:
            self.mutex.acquire()
            self._log(msg)
            self.mutex.release()

    def debug(self, msg):
        if self.loglevel >= LOG_DEBUG:
            self.mutex.acquire()
            self._debug(msg)
            self.mutex.release()

    def _log(self, msg):
        print(msg, flush=True)

    def _debug(self, msg):
        print("DEBUG: {}".format(msg), flush=True)


class SyslogLogger(Logger):
    def __init__(self, loglevel, ident=None):
        super().__init__(loglevel)
        if ident:
            syslog.openlog(ident)

    def _log(self, msg):
        syslog.syslog(msg)

    def _debug(self, msg):
        syslog.syslog("DEBUG: {}".format(msg))
