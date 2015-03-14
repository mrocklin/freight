import socket
import zmq
from functools import partial

try:
    from cPickle import dumps, loads, HIGHEST_PROTOCOL
except ImportError:
    from pickle import dumps, loads, HIGHEST_PROTOCOL
import threading

context = zmq.Context()


class ComputeNode(object):
    """ Serve simple computation via ZeroMQ

    Requests to self.uri take the form of an s-expression

        ('function-name', arg1, arg2, arg3, ...)

    This function name maps to the ``function`` dictionary.

    This node will then deserialize the input, map the name to the appropriate
    function, serialize the output, and send back the result.

    Serialization/deserialization is pluggable with loads/dumps methods

    Example
    -------

    >>> def inc(i):
    ...     return i + 1

    >>> def dec(i):
    ...     return i - 1

    >>> n = ComputeNode(host='localhost', port=5555,
    ...                 functions={'inc': inc, 'dec': dec})

    >>> import zmq
    >>> context = zmq.Context()
    >>> socket = context.socket(zmq.REQ)
    >>> socket.connect(n.url)

    >>> socket.send(dumps(('inc', 1)))
    >>> loads(socket.recv())
    2

    >>> socket.send(dumps(('close',)))  # Shutdown signal

    host: string
        The name of this machine
    port: int
        The port on which I listen
    server: zmq.Socket
        The server on which we listen for requests
    """
    def __init__(self, port=None, host=None, functions=None,
                 dumps=partial(dumps, protocol=HIGHEST_PROTOCOL),
                 loads=loads):
        self.host = host or socket.gethostname()
        self.port = int(port)
        self.loads = loads
        self.dumps = dumps

        if isinstance(functions, (tuple, list)):
            return dict((f.__name__, f) for f in functions)
        assert isinstance(functions, dict)
        functions = functions.copy()
        functions['close'] = self.close
        self.functions = functions

        self.start()

    def handle(self):
        """ Receive message, dispatch internally, send response """
        if self.server.closed:
            raise Exception()

        request = self.server.recv()
        request = self.loads(request)
        assert isinstance(request, tuple)

        func, args = request[0], request[1:]
        func = self.functions[func]

        result = func(*args)
        response = result
        self.server.send(self.dumps(response))

    @property
    def url(self):
        return 'tcp://%s:%d' % (self.host, self.port)

    def event_loop(self):
        """ Keep handling messages on our server/input socket """
        self._stop = False
        while not self._stop:
            self.handle()

    def close(self):
        self._stop = True

    def start(self):
        self.server = context.socket(zmq.REP)
        self.server.bind("tcp://*:%s" % self.port)
        self.thread = threading.Thread(target=self.event_loop)
        self.thread.start()

    def stop(self):
        sock = context.socket(zmq.REQ)
        sock.connect(self.url)
        sock.send(self.dumps(('close',)))
        self.thread.join()
        self.server.close()

    def __del__(self):
        self.stop()
