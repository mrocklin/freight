Freight
=======

A distributed collection of dictionaries (or other Mappings) intended to hold
and coordinate distributed storage of large blobs (like NumPy arrays.)

Freight keeps key location information centralized in a Redis server but uses
point-to-point communication to move data between worker nodes.  This is
useful when you have a small number of keys that associate to large values.

A single warehouse is a hosted dictionary with links to other warehouses.  It
combines the following fields:

* `data`         - a local MutableMapping
* `local_server` - a local ComputeNode serving data from self.data via ZeroMQ
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

In [3]: from freight import Warehouse

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

Name
----

The name was originally a play on [`chest`](http://github.com/mrocklin/chest)
another MutableMapping project.  Warehouses are where lots of chests live.
They're also part of a distribution network.

Now that I've spent more than five minutes thinking about it though I find
that this name conflicts with a Python Packaging Authority project, so I'll
have to find something new.  Suggestions welcome, particularly if they are
aligned with the "place to put things" theme of shelve/chest and the idea of
logistics and data transfer.

I've renamed this project to `freight`.


Why?
----

I built this mostly to learn about Redis and ZeroMQ.  This is a Saturday
morning project.  Please don't expect anything.

At some point I might use this for distributed
[`dask`](http://dask.pydata.org/) workloads.


What doesn't work
-----------------

Many things!  But mostly transactional security.  I wouldn't use thit to run a
bank or power a government.  In pathological cases you may silently get wrong
answers.
