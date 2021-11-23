#!/usr/bin/python3

import asyncio
from functools import partial
from utils import *
from proxy import Proxy


class RedisHandler(asyncio.Protocol):
    def __init__(self, proxy: Proxy, *args, **kwargs):
        self.proxy = proxy
        super(RedisHandler, self).__init__(*args, **kwargs)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        proxy = self.proxy
        cache = proxy.get_Cache()
        redis_client = proxy.get_Redis_Client()

        message = data.decode()

        if 'GET' in message or 'get' in message:
            mlist = message.splitlines()
            key = mlist[4]
            # Found a key, process further
            value = cache.get(key)

            if value is None:
                # Did not find the key in cache, look in redis server.
                value = redis_client.get(key)
                if value is not None and value != "":
                    # Found a key, add to cache.
                    cache.add(key, value)

            if value:
                # key is found, send the response.
                value = value.decode()
                val_len = f"${len(value)}\r\n".encode()
                val = f"{value}\r\n".encode()
                self.transport.write(val_len)
                self.transport.write(val)
            else:
                # Key not found return Null Bulk String.
                self.transport.write(b"$-1\r\n")
        else:
            self.transport.write(b"-ERR unknown command\r\n")


def main(hostname='', port=6378):
    args = parse_args()

    capacity = args.capacity
    expiry = args.expiry
    clients = args.max_clients
    redis_addr = args.redis_address
    proxy = Proxy(capacity, expiry, clients, redis_addr)

    loop = asyncio.get_event_loop()

    handler = partial(RedisHandler, proxy)
    cs_obj = loop.create_server(handler, hostname, port)
    server = loop.run_until_complete(cs_obj)
    print("Listening on port {}".format(port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Keyboard intrupt, initiating shutdown")
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


if __name__ == '__main__':
    main()
