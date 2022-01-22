class PrefixLogger:
    def __init__(self, logger, prefix):
        self.logger = logger
        self.prefix = prefix

    def log(self, msg):
        self.logger.log("[{}] {}".format(self.prefix, msg))

    def debug(self, msg):
        self.logger.debug("[{}] {}".format(self.prefix, msg))
