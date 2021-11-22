import asyncio


class RedisServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        if 'GET' in message:
            self.transport.write(b"$3\r\n")
            self.transport.write(b"BAZ\r\n")
        else:
            self.transport.write(b"-ERR unknown command\r\n")


def main(hostname='localhost', port=6379):
    loop = asyncio.get_event_loop()
    coro = loop.create_server(RedisServerProtocol,
                              hostname, port)
    server = loop.run_until_complete(coro)
    print("Listening on port {}".format(port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("User requested shutdown.")
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
        print("Redis is now ready to exit.")
    return 0


if __name__ == '__main__':
    main()