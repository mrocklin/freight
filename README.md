Warehouse
=========

A distributed collection of dictionaries (or other Mappings) intended to hold
coordinate distributed storage of large blobs (like NumPy arrays.)

Warehouse keeps key location information centralized in a Redis server but uses
point-to-point communication to move data between worker nodes.  This is
useful when you have a small number of keys that associate to large values.

A single warehouse is a hosted dictionary with links to other warehouses.  It
combines the following fields:

* `data`         - a local MutableMapping
* `local_server` - a local ComputeNode serving data from self.data via `0mq`
* `redis_db`     - a connection to a Redis instance mapping keys to urls of
                   Warehouses that hold values of those keys

Several warehouses act in concert to provide a distributed bulk key-value
storage solution.


Example
-------

    $ redis-server

```python
In [1]: import redis

In [2]: r = redis.Redis()

In [3]: from warehouse import Warehouse

In [4]: A = Warehouse(redis_db=r, host='localhost', port=5001)

In [5]: B = Warehouse(redis_db=r, host='localhost', port=5002)

In [6]: C = Warehouse(redis_db=r, host='localhost', port=5003)

In [7]: A['one'] = 1

In [8]: A.data
Out[8]: {'one': 1}

In [9]: B.data
Out[9]: {}

In [10]: B['one']
Out[10]: 1
```
