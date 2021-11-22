""" Redis connector adapter class """

import redis
from redis.exceptions import ConnectionError


class BackendRedis:
    """
    This is a redis client implementation to comminicate with backend redis
    """

    def __init__(self, redis_address: str):
        host, port = redis_address.split(":")
        self.client = None
        self.error = "Connected"
        try:
            print(redis_address)
            conn = redis.Redis(host, port)
            conn.ping()
            self.client = conn
        except ConnectionError as err:
            self.error = "Connection Error " + str(err.__str__)

    def get(self, key: str) -> int:
        """ Get value associated with key from Redis Backend """
        try:
            key_value = self.client.get(key)
            return key_value
        except BaseException:
            return ""
