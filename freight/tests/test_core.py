from freight import Warehouse

import redis

from contextlib import contextmanager

@contextmanager
def redis_db(port=6379):
    r = redis.Redis(db=10, port=port)

    try:
        yield r
    finally:
        for key in r.keys():
            del r[key]


def test_core():
    with redis_db() as r:
        a = {'one': 1, 'three': 3}
        A = Warehouse(data=a, redis_db=r, port=5556)

        b = {'two': 2, 'three': 3}
        B = Warehouse(data=b, redis_db=r, port=5557)

        try:
            assert r.smembers('one') == set([A.local_server.url])
            assert r.smembers('three') == set([A.local_server.url,
                                               B.local_server.url])
            assert A['one'] == 1
            assert B['two'] == 2

            assert 'two' not in A.data
            assert A['two'] == 2
            assert B['one'] == 1

            assert 'one' in A
            assert 'two' in A

            assert 'four' not in A
            A['four'] = 4
            assert 'four' not in B.data
            assert B['four'] == 4
            assert 'four' in B.data

            del B['four']
            assert 'four' not in A

            assert set(A) == set(['one', 'two', 'three'])
            assert len(A) == len(B) == 3
        finally:
            A.local_server.stop()
            B.local_server.stop()
