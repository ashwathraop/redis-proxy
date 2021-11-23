#!/usr/bin/python3

import pytest
import time
import requests
import redis


CAPACITY = 5
KEY_EXPIRY = 5
HOST = 'localhost'
PORT = 8080
REDIS_HOST = "redis"
REDIS_PORT = 6379
MAX_CLIENTS = 5
BASE_URL = f"http://{HOST}:{PORT}/"
RESP_PORT = 6378


def test_connection():
    """ Test connection to Proxy Server """
    resp = requests.get(url=BASE_URL)
    print(resp.status_code)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"


def test_proxy_cache_get():
    """ Test for the correctness of proxy get operation """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    redis_client.set('year', 'its2021', 5)
    rv = redis_client.get('year').decode('utf-8')

    # Now make a GET request to Proxy and verify the key.
    url = BASE_URL + 'year'
    resp = requests.get(url=url)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"
    assert rv == resp.text, f"Expected value: {rv}, got {resp.text}"


def test_proxy_lru_eviction():
    """ Test for cache lru eviction of a key """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    for i in range(MAX_CLIENTS+1):
        redis_client.set(f'key{i}', f'value{i}', 20)

    # Now make a GET requests to Proxy and get the values.
    for i in range(MAX_CLIENTS+1):
        url = BASE_URL + f'key{i}'
        resp = requests.get(url=url)
        assert resp.ok, "Expected success in response but got error"
        assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"

    # Update the redis db with new values.
    for i in range(MAX_CLIENTS+1):
        redis_client.set(f'key{i}', f'new_value{i}', 20)

    # Request to cache now should return updated value if LRU worked.
    url = BASE_URL + 'key0'
    resp = requests.get(url=url)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"
    assert 'new_value0' == resp.text, f"Expected value: new_value0, got {resp.text}"


def test_proxy_cache_expiry():
    """ Test for cache expiry of a key """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    redis_client.set('date', '11/21/2021', 10)

    # Now make a GET request to Proxy and get the value.
    url = BASE_URL + 'date'
    resp = requests.get(url=url)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"

    # Update the redis with new value and wait for the cache to expire.
    rv = '11/22/2021'
    redis_client.set('date', rv, 60)
    time.sleep(KEY_EXPIRY+2)

    # Verify the key now
    resp = requests.get(url=url)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"
    assert rv == resp.text, f"Expected value: {rv}, got {resp.text}"


def test_proxy_cache_correctness():
    """ Test for correctness of cache data """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    redis_client.set('date', '11/21/2021', 10)

    # Now make a GET request to Proxy and get the value.
    url = BASE_URL + 'date'
    resp = requests.get(url=url)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"
    cache_value = resp.text

    # Update the redis with new value.
    redis_client.set('date', '11/22/2021', 10)

    # Verify the cache now.
    resp = requests.get(url=url)
    assert resp.ok, "Expected success in response but got error"
    assert resp.status_code == 200, f"Expected status_code: 200, got {resp.status_code}"
    assert cache_value == resp.text, f"Expected value: {cache_value}, got {resp.text}"


def test_proxy_key_not_found():
    """ request for a non exitent key """
    # Make a GET request to Proxy and get the value.
    url = BASE_URL + 'name'
    resp = requests.get(url=url)
    assert not resp.ok, "Expected error in response but got success"
    assert resp.status_code == 404, f"Expected status_code: 404, got {resp.status_code}"


def test_proxy_resp_cache_get():
    """ Test for the correctness of RESP proxy get operation """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    redis_client.set('year', '2021', 5)
    rv = redis_client.get('year').decode('utf-8')

    resp_client = redis.Redis(HOST, RESP_PORT)
    # Now make a GET request to Proxy and verify the key.
    res = resp_client.get('year').decode('utf-8')
    assert rv == res, f"Expected value: {rv}, got {res}"


def test_proxy_resp_key_not_found():
    """ request for a non exitent key """
    # Make a GET request to Proxy and get the value.
    resp_client = redis.Redis(HOST, RESP_PORT)
    # Now make a GET request to Proxy and verify the key.
    res = resp_client.get('dates')
    assert res == None, f"Expected value: None, got {res}"


def test_proxy_resp_lru_eviction():
    """ Test for cache lru eviction of a key """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    resp_client = redis.Redis(HOST, RESP_PORT)

    for i in range(MAX_CLIENTS+1):
        redis_client.set(f'key{i}', f'value{i}', 20)

    res = resp_client.get('year').decode('utf-8')
    # Now make a GET requests to Proxy and get the values.
    for i in range(MAX_CLIENTS+1):
        res = resp_client.get(f'key{i}').decode('utf-8')

    # Update the redis db with new values.
    for i in range(MAX_CLIENTS+1):
        redis_client.set(f'key{i}', f'new_value{i}', 20)

    # Request to cache now should return updated value if LRU worked.
    res = resp_client.get('key0').decode('utf-8')
    assert 'new_value0' == res, f"Expected value: new_value0, got {res}"


def test_proxy_resp_cache_expiry():
    """ Test for cache expiry of a key """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    resp_client = redis.Redis(HOST, RESP_PORT)

    redis_client.set('date', '11/21/2021', 10)

    # Now make a GET request to Proxy and get the value.
    res = resp_client.get('date').decode('utf-8')

    # Update the redis with new value and wait for the cache to expire.
    rv = '11/22/2021'
    redis_client.set('date', rv, 60)
    time.sleep(KEY_EXPIRY+2)

    # Verify the key now
    res = resp_client.get('date').decode('utf-8')
    assert rv == res, f"Expected value: {rv}, got {res}"


def test_proxy_resp_cache_correctness():
    """ Test for correctness of cache data """
    # Connect to backend redis and set a key
    redis_client = redis.Redis(REDIS_HOST, REDIS_PORT)
    resp_client = redis.Redis(HOST, RESP_PORT)

    redis_client.set('date', '11/21/2021', 10)

    # Now make a GET request to Proxy and get the value.
    res = resp_client.get('date').decode('utf-8')
    cache_value = res

    # Update the redis with new value.
    redis_client.set('date', '11/22/2021', 10)

    # Verify the cache now.
    res = resp_client.get('date').decode('utf-8')
    assert cache_value == res, f"Expected value: {cache_value}, got {res}"
