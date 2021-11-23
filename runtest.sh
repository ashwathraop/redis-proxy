#!/bin/sh

CAPACITY=5
GLOBAL_EXPIRY=5
HOST='localhost'
PORT=8080
REDIS_ADDRESS="redis:6379"
MAX_CLIENTS=5

python3 src/proxy.py -c $CAPACITY -e $GLOBAL_EXPIRY -p $PORT -m $MAX_CLIENTS -r $REDIS_ADDRESS &> /dev/null &
python3 src/resp.py -c $CAPACITY -e $GLOBAL_EXPIRY -p $PORT -m $MAX_CLIENTS -r $REDIS_ADDRESS &> /dev/null &
pytest -v --disable-pytest-warnings 
