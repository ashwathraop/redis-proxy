#!/usr/bin/python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
from functools import partial
from backredis import BackendRedis
from utils import *
from cache import LRUCache


class Proxy:
    def __init__(self, capacity: int, expiry: int, clients: int, redis_address: str) -> None:
        self.cache = LRUCache(capacity, expiry)
        self.redis = BackendRedis(redis_address)
        self.semaphore = threading.Semaphore(clients)

    def get_Cache(self):
        return self.cache

    def get_Redis_Client(self):
        return self.redis

    def get_Semaphore(self):
        return self.semaphore


class GetHandler(BaseHTTPRequestHandler):
    def __init__(self, proxy: Proxy, *args, **kwargs):
        self.proxy = proxy
        super(GetHandler, self).__init__(*args, **kwargs)

    def do_GET(self):
        """ GET handler function """ 
        proxy = self.proxy
        semaphore = proxy.get_Semaphore()
        cache = proxy.get_Cache()
        redis_client = proxy.get_Redis_Client()

        if semaphore.acquire(blocking=False):
            # Get the key from request path url
            key = self.path.split("/")[1]

            if key == "":
                # Empty request, show usage.
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Redis Proxy - ")  # return data in bytes
                self.wfile.write(
                    b"Usage: GET /key - fetches key from the redis server")
            else:
                # Found a key, process further
                value = cache.get(key)

                if value is None:
                    # Did not find the key in cache, look in redis server.
                    value = redis_client.get(key)
                    if value != "":
                        # Found a key, add to cache.
                        cache.add(key, value)

                if value:
                    # key is found, send the response.
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(value)
                else:
                    self.send_error(404, f"Requested Key: {key} not found")

            # Release the lock
            semaphore.release()
        else:
            # Couldnt get a lock so send back error about exceeding max client limit.
            self.send_error(
                429, "Requests exceeded the limit that can be served by the proxy")


class ThreadingHttpProxy(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class HttpProxy():
    """ Instantiate Proxy and start Http Server in multithreaded mode """

    def __init__(self, addr: str, port: int, capacity: int, expiry: int, clients: int, redis_address: str) -> None:
        self.addr = addr
        self.port = port
        self.proxy = Proxy(capacity, expiry, clients, redis_address)
        server_address = (addr, port)

        handler = partial(GetHandler, self.proxy)
        self.server = ThreadingHttpProxy(server_address, handler)

    def start(self):
        """ Start the http server """
        print(f"Starting httpd server on {self.addr}:{self.port}")
        self.server.serve_forever()


def main():
    args = parse_args()

    capacity = args.capacity
    expiry = args.expiry
    port = args.port
    max_cnt = args.max_clients
    redis_addr = args.redis_address

    server = HttpProxy('', port, capacity, expiry, max_cnt, redis_addr)
    server.start()


if __name__ == "__main__":
    main()
