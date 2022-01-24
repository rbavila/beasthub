import threading
import queue
import beasthub.logger
import beasthub.net

from beasthub.dispatcher import Dispatcher

class BEASTHub(threading.Thread):
    def __init__(self, name, logger, inputs, outputs):
        super().__init__(name=name, daemon=True)
        self.logger = logger
        self.inputs = inputs
        self.outputs = outputs
        self.msgqueue = queue.SimpleQueue()
        self.input_workers = []
        self.output_workers = []

    def run(self):
        # create input workers
        for i in self.inputs:
            name = "in {}".format(":".join(i))
            [proto, *middleparams, port_str] = i
            port = int(port_str)
            if proto == "tcp":
                [tcptype, *hostparam] = middleparams
                host = hostparam[0] if len(hostparam) > 0 else "0.0.0.0"
                if tcptype == "listen":
                    t = beasthub.net.TCPListenerInputManager(name, self.logger, host, port, self.msgqueue)
                else:
                    t = beasthub.net.TCPConnectorInput(name, self.logger, host, port, self.msgqueue)
            else:
                host = middleparams[0] if len(middleparams) > 0 else "0.0.0.0"
                t = beasthub.net.UDPInput(name, self.logger, host, port, self.msgqueue)
            self.input_workers.append(t)

        # create output workers
        for o in self.outputs:
            name = "out {}".format(":".join(o))
            [proto, *middleparams, port_str] = o
            port = int(port_str)
            if proto == "tcp":
                [tcptype, *hostparam] = middleparams
                host = hostparam[0] if len(hostparam) > 0 else "0.0.0.0"
                if tcptype == "listen":
                    t = beasthub.net.TCPListenerOutputManager(name, self.logger, host, port, self.msgqueue)
                else:
                    t = beasthub.net.TCPConnectorOutput(name, self.logger, host, port)
            else:
                host = middleparams[0] if len(middleparams) > 0 else "0.0.0.0"
                t = beasthub.net.UDPOutput(name, self.logger, host, port)
            self.output_workers.append(t)

        # create the dispatcher thread
        name = "dispatcher"
        self.dispatcher = Dispatcher(name, self.logger, self.msgqueue, self.output_workers)

        # start all threads
        self.dispatcher.start()
        for t in self.input_workers:
            t.start()
        for t in self.output_workers:
            t.start()

        # wait for all threads to shutdown
        for t in self.input_workers:
            t.join()
        for t in self.output_workers:
            t.join()
        self.dispatcher.join()
        self.logger.log("Done")

    def shutdown(self):
        self.logger.log("Received interrupt signal, waiting for threads to shut down")
        for t in self.input_workers:
            t.shutdown()
        for t in self.output_workers:
            t.shutdown()
        self.dispatcher.shutdown()
