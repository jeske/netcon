#!/neo/opt/bin/python
"""TCP client class borrowed from the httpdru.py

Example:

"""

import socket
import select
import string
import errno


class TCP:
    """This class manages a connection to an TCP server."""

    def __init__(self, host, port):
        """Initialize a new instance.

        If specified, `host' is the name of the remote host to which
        to connect.  If specified, `port' specifies the port to which
        to connect.  By default, httplib.HTTP_PORT is used.

        """
        self.debuglevel = 0
        self.valid = None
        if host:
            self.connect(host, port=port)

    def set_debuglevel(self, debuglevel):
        """Set the debug output level.

        A non-false value results in debug messages for connection and
        for all messages sent to and received from the server.

        """
        self.debuglevel = debuglevel

    def connect(self, host, port = 0):
        """Connect to a host on a given port.

        Note:  This method is automatically invoked by __init__,
        if a host is specified during instantiation.

        """
        if not port:
            i = string.find(host, ':')
            if i >= 0:
                host, port = host[:i], host[i+1:]
                try: port = string.atoi(port)
                except string.atoi_error:
                    raise socket.error, "nonnumeric port"
        if not port:
            port = 22


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(0)

        if self.debuglevel > 0:
            print 'connect:', (host, port)

        # This is kinda ugly, but a non-blocking connect() returns
        # errno 36 ('Operation now in progress') and we don't want to
        # catch that as an error.  So we let select() notify us
        # of a complete connection
        try:
            result = self.sock.connect( (host, port) )
        except socket.error, val:
            if val[0] == errno.EINPROGRESS or (sys.platform == "win32" and val[0] == errno.WSAEWOULDBLOCK):
            # 'Operation in Progress' is OK
                pass
            else:
                self.valid = None
                return

        # wait for the connect to succeed, or time out in 10s
        try:
            (sread, swrite, serror) = select.select( [], [self.sock], [], 10 )
        except select.error:
            # there was a problem ...
            # print "Select error %s: %s" (select.error)
            self.valid = None
            return

        if swrite.count(self.sock) > 0 :
            # Check the socket for an error
            # we got the connection...if there was no error
            i = self.sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if 0 == i:
                self.valid = 1
                self.sock.setblocking(1)
                return

        # otherwise, we hit the timeout
        self.valid = None


    def send(self, str):
        """Send `str' to the server."""
        if self.debuglevel > 0: print 'send:', `str`
        self.sock.send(str)


    def getreply(self, timeout):
        """Get a reply from the server.

        Returns a tuple consisting of:
        - server response code (e.g. '200' if all goes well)
        - server response string corresponding to response code

        """

        x = select.select([self.sock], [], [], timeout)
        if ([], [], []) == x:
            return -2, -2

        # Receive up to 256 bytes
        line = self.sock.recv(256)
        if self.debuglevel > 0: print 'reply:', `line`
        errcode = 0
        msg = line
        return errcode, msg

    def close(self):
        """Close the connection to the HTTP server."""
        if self.sock:
            self.sock.close()
        self.sock = None


def test():
    """Test this module.

    The test consists of retrieving and displaying the Python
    home page, along with the error code and error string returned
    by the www.python.org server.

    """
    import sys
    import getopt
    opts, args = getopt.getopt(sys.argv[1:], 'd')
    dl = 0
    for o, a in opts:
        if o == '-d': dl = dl + 1
    host = 'www.python.org'
    if args[0:]: host = args[0]
    t = TCP(host,80)
    t.set_debuglevel(1)
    t.send("GET / HTTP/1.1\nHost: www.python.org\n\n")
    print 'Valid: %s' % (t.valid)
    errcode, errmsg = t.getreply(45)
    print 'errcode =', errcode
    print 'errmsg  =', errmsg
    print


if __name__ == '__main__':
    test()
