# beasthub

This is a tool to replicate multiple BEAST protocol inputs to
multiple outputs.

At least one input and one output are required.  These take the
form `<'in'|'out'>:<proto>:[<tcptype>:][<host>:]<port>`, where:

* `<proto>` = 'tcp' or 'udp'
* `<tcptype>` = 'listen' or 'connect' (valid only for TCP)
* `<host>` = name or IP address (currently only IPv4 is supported)
* `<port>` = port number


## Usage examples:

`$ beasthub in:tcp:connect:10.0.0.1:30005 out:udp:10.0.0.2:12345`
    Read BEAST messages via TCP from host 10.0.0.1 and send them
    via UDP to host 10.0.0.2

`$ beasthub in:udp:31005 out:udp:10.0.0.2:12345 out:tcp:connect:10.0.0.3:5555`  
    Receive messages via UDP and send them to both hosts 10.0.0.2 (via UDP)
    and 10.0.0.3 (via TCP)


## Examples of all possible in/out variations:

`in:tcp:listen:1234`
    Listen for connections on port 1234 and then read BEAST messages
    from clients that connect.

`in:tcp:listen:192.168.0.1:1234`
    Similar to the previous option but only binds to the given IP address.

`in:tcp:connect:10.0.0.1:1234`
    Connect to the remote host on port 1234 and read BEAST messages from it.

`in:udp:1234`
    Receive BEAST messages on the given UDP port.

`in:udp:192.168.0.1:1234`
    Similar to the previous option but only binds to the given IP address.

`out:tcp:listen:1234`
    Listen for connections on port 1234 and then send BEAST messages
    to clients that connect.

`out:tcp:listen:192.168.0.1:1234`
    Similar to the previous option but only binds to the given IP address.

`out:tcp:connect:10.0.0.1:1234`
    Connect to the remote host on port 1234 and send BEAST messages to it.

`out:udp:10.0.0.1:1234`
    Send BEAST messages to the given host on the given UDP port.


## Installation

`$ pip install .`
