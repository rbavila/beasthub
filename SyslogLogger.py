from Logger import Logger
import syslog

class SyslogLogger(Logger):
    def __init__(self, loglevel, ident=None):
        super().__init__(loglevel)
        if ident:
            syslog.openlog(ident)

    def _log(self, msg):
        syslog.syslog(msg)

    def _debug(self, msg):
        syslog.syslog("DEBUG: {}".format(msg))
