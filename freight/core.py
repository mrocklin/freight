from zmqompute import ComputeNode
import zmq
from redis import Redis
from collections import MutableMapping

context = zmq.Context()

class Warehouse(MutableMapping):
    """ A Hosted dictionary with links to other dictionaries

    A warehouse is a combination of the following

    * data - a local MutableMapping
    * local_server - a local ComputeNode serving data from self.data
    * redis_db - a connection to a Redis instance mapping keys to urls of
                 Warehouses that hold values of those keys

    Several warehouses act in concert to provide a distributed bulk key-value
    storage solution.
    """
    def __init__(self, data=None, redis_db=None, host=None, port=None):
        self.data = data if data is not None else dict()
        self.redis_db = redis_db if redis_db is not None else Redis()
        self.local_server = ComputeNode(host=host, port=port,
                                    functions={'get': self.data.get,
                                               'delete': self.data.__delitem__})
        for key in self.data:
            self.redis_db.sadd(key, self.local_server.url)

    def __del__(self):
        del self.local_server

    def get(self, key):
        try:
            return self.data[key]
        except KeyError:
            others = self.redis_db.smembers(key)
            if not others:
                raise KeyError("Key not found")
            other = next(iter(others))
            socket = context.socket(zmq.REQ)
            socket.connect(other)
            socket.send(self.local_server.dumps(('get', key)))
            payload = self.local_server.loads(socket.recv())
            self.data[key] = payload  # store locally
            return payload

    def __getitem__(self, key):
        return self.get(key)

    def __contains__(self, key):
        return key in self.data or key in self.redis_db

    def set(self, key, value):
        if key in self:
            raise KeyError("Duplicate key found")
        self.data[key] = value
        self.redis_db.sadd(key, self.local_server.url)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __delitem__(self, key):
        if key in self.data:
            del self.data[key]

        socks = []
        for other in self.redis_db.smembers(key):
            socket = context.socket(zmq.REQ)
            socket.connect(other)
            socket.send(self.local_server.dumps(('delete', key)))
            socks.append(socket)
        for sock in socks:
            payload = self.local_server.loads(sock.recv())

        self.redis_db.delete(key)

    def __iter__(self):
        local_keys = set(self.data.keys())
        for key in local_keys:  # Yield our local keys first
            yield key

        for key in self.redis_db.keys():  # Yield remote keys afterwards
            if key not in local_keys:
                yield key

    def __len__(self):
        # TODO: inspect self.redis_db.info()
        return sum(1 for i in self)
