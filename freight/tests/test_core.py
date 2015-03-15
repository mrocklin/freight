from freight import Warehouse

import redis

from contextlib import contextmanager

@contextmanager
def redis_db(port=6379):
    r = redis.Redis(db=10, port=port)

    try:
        yield r
    finally:
        r.flushall()


@contextmanager
def two_node(a=None, b=None):
    with redis_db() as r:
        if a is None:
            a = dict()
        if b is None:
            b = dict()

        A = Warehouse(data=a, redis_db=r, port=5556)
        B = Warehouse(data=b, redis_db=r, port=5557)

        try:
            yield (r, A, B)
        finally:
            try:
                A.local_server.stop()
            except:
                pass
            try:
                B.local_server.stop()
            except:
                pass


def test_core():
    with two_node({'one': 1, 'three': 3}, {'two': 2, 'three': 3}) as (r, A, B):
        assert r.smembers('one') == set([A.local_server.url])
        assert r.smembers('three') == set([A.local_server.url,
                                           B.local_server.url])
        assert A['one'] == 1
        assert B['two'] == 2

        assert 'two' not in A.data
        assert A['two'] == 2
        assert B['one'] == 1

def test_contains():
    with two_node({'one': 1, 'three': 3}, {'two': 2, 'three': 3}) as (r, A, B):
        assert 'one' in A
        assert 'two' in A
        assert 'one' in B
        assert 'two' in B


def test_transfer():
    with two_node({'one': 1, 'three': 3}, {'two': 2, 'three': 3}) as (r, A, B):
        A['four'] = 4
        assert 'four' not in B.data
        assert B['four'] == 4
        assert 'four' in B.data


def test_delitem():
    with two_node({'one': 1, 'three': 3}, {'two': 2, 'three': 3}) as (r, A, B):
        del B['four']
        assert 'four' not in A


def test_iter_len():
    with two_node({'one': 1, 'three': 3}, {'two': 2, 'three': 3}) as (r, A, B):
        assert set(A) == set(['one', 'two', 'three'])
        assert len(A) == len(B) == 3


def test_del():
    with two_node({'one': 1, 'three': 3}, {'two': 2, 'three': 3}) as (r, A, B):
        url = B.local_server.url
        assert r.sismember('three', url)
        B.__del__()
        assert not r.sismember('three', url)
