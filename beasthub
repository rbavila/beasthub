#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import signal
import sys
import argparse
import textwrap
from queue import SimpleQueue
from Logger import Logger
from SyslogLogger import SyslogLogger
from PrefixLogger import PrefixLogger
from TCPListenerInputManager import TCPListenerInputManager
from TCPListenerOutputManager import TCPListenerOutputManager
from TCPConnectorInput import TCPConnectorInput
from TCPConnectorOutput import TCPConnectorOutput
from UDPInput import UDPInput
from UDPOutput import UDPOutput
from Dispatcher import Dispatcher


#
# handle interruptions (ex.: Ctrl-C)
#
def sig_handler(sig, frame):
    main_logger.log("Received interrupt signal, waiting for threads to shut down")
    # tell all threads to shutdown
    for t in input_workers:
        t.shutdown()
    for t in output_workers:
        t.shutdown()
    dispatcher.shutdown()

#
# main
#
signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
        This is a tool to replicate multiple BEAST protocol inputs to
        multiple outputs.

        At least one input and one output are required.  These take the
        form 'in|out:<proto>:[<tcptype>:][<host>:]<port>', where:

        <proto> = 'tcp' or 'udp'
        <tcptype> = 'listen' or 'connect' (valid only for TCP)
        <host> = name or IP address (currently only IPv4 is supported)
        <port> = port number


        Usage examples:

        $ %(prog)s in:tcp:connect:10.0.0.1:30005 out:udp:10.0.0.2:12345
            Read BEAST messages via TCP from host 10.0.0.1 and send them
            via UDP to host 10.0.0.2

        $ %(prog)s in:udp:31005 out:udp:10.0.0.2:12345 out:tcp:connect:10.0.0.3:5555
            Receive messages via UDP and send them to both hosts 10.0.0.2 (via UDP)
            and 10.0.0.3 (via TCP)


        Examples of all possible in/out variations:

        in:tcp:listen:1234
            Listen for connections on port 1234 and then read BEAST messages
            from clients that connect.

        in:tcp:listen:192.168.0.1:1234
            Similar to the previous option but only binds to the given IP address.

        in:tcp:connect:10.0.0.1:1234
            Connect to the remote host on port 1234 and read BEAST messages from it.

        in:udp:1234
            Receive BEAST messages on the given UDP port.

        in:udp:192.168.0.1:1234
            Similar to the previous option but only binds to the given IP address.

        out:tcp:listen:1234
            Listen for connections on port 1234 and then send BEAST messages
            to clients that connect.

        out:tcp:listen:192.168.0.1:1234
            Similar to the previous option but only binds to the given IP address.

        out:tcp:connect:10.0.0.1:1234
            Connect to the remote host on port 1234 and send BEAST messages to it.

        out:udp:10.0.0.1:1234
            Send BEAST messages to the given host on the given UDP port.


        ''')
)
parser.add_argument("inout", nargs="+", metavar="IN|OUT",
#    help="An input or output in the form in|out:<proto>:[<tcptype>:][<host>:]<port>")
    help=argparse.SUPPRESS)
parser.add_argument("-S", "--syslog", action="store_true", help="Log messages to syslog instead of stdout")
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true", help="Show extra/debugging messages")
group.add_argument("-q", "--quiet", action="store_true", help="Be completely quiet")
args = parser.parse_args()


inputs = []
outputs = []
for arg in args.inout:
    [type, proto, *remainder] = arg.split(":")
    if not (proto == "tcp" or proto == "udp"):
        raise Exception("Unsupported protocol {}".format(proto))
    if proto == "tcp" and \
            not (remainder[0] == "listen" or remainder[0] == "connect"):
        raise Exception("TCP type must be either 'listen' or 'connect'")
    if type == "in":
        inputs.append([proto, *remainder])
    elif type == "out":
        outputs.append([proto, *remainder])
    else:
        raise Exception("Arguments must begin with either 'in' or 'out'")
if len(inputs) == 0 or len(outputs) == 0:
    raise Exception("At least one input and one output must be given.")


#
# create the logger
#
if args.quiet:
    loglevel = Logger.LOG_QUIET
elif args.verbose:
    loglevel = Logger.LOG_DEBUG
else:
    loglevel = Logger.LOG_INFO

if args.syslog:
    logger = SyslogLogger(loglevel, "beasthub")
else:
    logger = Logger(loglevel)
main_logger = PrefixLogger(logger, "main")
main_logger.log("Starting")

#
# create the main message queue
#
msgqueue = SimpleQueue()

#
# create input workers
#
input_workers = []
for [proto, *remainder] in inputs:
    if proto == "tcp":
        [tcptype, *host, port] = remainder
        if tcptype == "listen":
            if len(host) == 0:
                host = ["0.0.0.0"]
                name = "in tcp:listen:{}".format(port)
            else:
                name = "in tcp:listen:{}:{}".format(host[0], port)
            t_logger = PrefixLogger(logger, name)
            t = TCPListenerInputManager(name, t_logger, host[0], int(port), msgqueue)
        else:
            name = "in tcp:connect:{}:{}".format(host[0], port)
            t_logger = PrefixLogger(logger, name)
            t = TCPConnectorInput(name, t_logger, host[0], int(port), msgqueue)
    else:
        [*host, port] = remainder
        if len(host) == 0:
            host = ["0.0.0.0"]
            name = "in udp:{}".format(port)
        else:
            name = "in udp:{}:{}".format(host[0], port)
        t_logger = PrefixLogger(logger, name)
        t = UDPInput(name, t_logger, host[0], int(port), msgqueue)
    input_workers.append(t)

#
# create output workers
#
output_workers = []
for [proto, *remainder] in outputs:
    if proto == "tcp":
        [tcptype, *host, port] = remainder
        if tcptype == "listen":
            if len(host) == 0:
                host = ["0.0.0.0"]
                name = "out tcp:listen:{}".format(port)
            else:
                name = "out tcp:listen:{}:{}".format(host[0], port)
            t_logger = PrefixLogger(logger, name)
            t = TCPListenerOutputManager(name, t_logger, host[0], int(port), msgqueue)
        else:
            name = "out tcp:connect:{}:{}".format(host[0], port)
            t_logger = PrefixLogger(logger, name)
            t = TCPConnectorOutput(name, t_logger, host[0], int(port))
    else:
        [host, port] = remainder
        name = "out udp:{}:{}".format(host, port)
        t_logger = PrefixLogger(logger, name)
        t = UDPOutput(name, t_logger, host, int(port))
    output_workers.append(t)

#
# create the dispatcher thread
#
name = "dispatcher"
d_logger = PrefixLogger(logger, name)
dispatcher = Dispatcher(name, d_logger, msgqueue, output_workers)

#
# start everybody
#
dispatcher.start()
for t in input_workers:
    t.start()
for t in output_workers:
    t.start()

#
# wait for all threads to shutdown
#
for t in input_workers:
    t.join()
for t in output_workers:
    t.join()
dispatcher.join()
main_logger.log("Done")
