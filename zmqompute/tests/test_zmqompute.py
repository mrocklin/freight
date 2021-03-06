from zmqompute import ComputeNode
from contextlib import contextmanager
from pickle import dumps, loads
import zmq

port = 5455
context = zmq.Context()

def inc( i):
    return i + 1

def dec(i):
    return i - 1


@contextmanager
def incdec_at(port):
    n = ComputeNode(port=port, host='localhost',
                    functions={'inc': inc, 'dec': dec})
    try:
        yield n
    finally:
        if not n._stop:
            n.stop()


def test_inc_dec():
    port = 5465
    with incdec_at(port) as node:
        socket = context.socket(zmq.REQ)
        socket.connect(node.url)

        socket.send(dumps(('inc', 1)))
        assert loads(socket.recv()) == 2

        socket.send(dumps(('dec', 2)))
        assert loads(socket.recv()) == 1

        socket.send(dumps(('close',)))
        assert loads(socket.recv()) == None

        assert node._stop


def test_cleanup_on_del():
    port = 5466
    with incdec_at(port) as node:
        node.__del__()
        assert node._stop
