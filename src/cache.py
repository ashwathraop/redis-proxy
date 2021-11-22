""" LRU cache implemetation with connection to backend redis """

from _thread import RLock
from collections import OrderedDict
import time


class LRUCache:
    """
    This is a thread safe implementation of LRU cache based on OrderedDict
    """

    def __init__(self, capacity: int, expiry: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.expiry = expiry
        self.lock = RLock()

    def get(self, key: int) -> int:
        """ Get the key from cache """
        with self.lock:
            if key not in self.cache:
                return None

            value, key_expiry = self.cache[key]
            time_now = time.time()*1000.0

            if key_expiry - time_now >= 0:
                self.cache.move_to_end(key)
                return value

            # If we are here, then key is expired. Delete and return.
            del self.cache[key]
            return None

    def add(self, key: int, value: int) -> None:
        """ Add a new entry to the cache """
        time_now = time.time()*1000.0
        key_expiry = (self.expiry*1000.0) + time_now
        key_value = [value, key_expiry]

        with self.lock:
            if key in self.cache:
                self.cache[key] = key_value
                self.cache.move_to_end(key)
                return

            # if the cache is full, evict LRU key.
            if len(self.cache) >= self.capacity:
                lru_key = next(iter(self.cache))
                del self.cache[lru_key]

            self.cache[key] = key_value
