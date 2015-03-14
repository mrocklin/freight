Warehouse
=========

A distributed collection of dictionaries (or other Mappings)

Example
-------

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
