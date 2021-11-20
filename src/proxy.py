from utils import *
from cache import LRUCache


class HttpProxy:
    def __init__(self) -> None:
        pass


def main():
    args = parse_args()

    capacity = args.capacity
    expiry = args.expiry
    port = args.port
    mc = args.max_clients
    ra = args.redis_address


if __name__ == "__main__":
    main()
