import argparse


def parse_args():
            # Create the parser
    parser = argparse.ArgumentParser()  # Add an argument
    parser.add_argument('-c',
                        # '--capacity',
                        dest="capacity",
                        default=100,
                        type=int,
                        help="Cache capacity (number of keys)")
    parser.add_argument('-e',
                        dest='expiry',
                        default=3600,
                        type=int,
                        help="Cache expiry (time in seconds)")
    parser.add_argument('-r',
                        dest='redis_address',
                        default="redis:6379",
                        help="Backend Redis (address:port)")
    parser.add_argument('-p',
                        dest='port',
                        type=int,
                        default=8080,
                        help="Port the proxy server listens on")
    parser.add_argument('-m',
                        dest='max_clients',
                        default=5,
                        type=int,
                        help="Maximum number of clients served by the proxy")
    return parser.parse_args()
