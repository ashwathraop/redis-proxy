import redis


class BackenRedis:
    """
    This is a redis client implementation to comminicate with backend redis
    """

    def __init__(self, host: str, port: int):
        self.client = None
        self.error = ""
        try:
            conn = redis.Redis(host, port)
            conn.ping()
            self.client = conn
        except:
            self.error = "Connection Error"

    def Get(self, key: str) -> int:
        key_value = self.client.get(key)
        return key_value[0]
