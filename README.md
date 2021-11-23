# redis-proxy
A transparent Redis proxy service.

Features:
- HTTP web service - redis like GET command calls through a HTTP GET request
- Cached GET - GET requests processed through an in-memory LRU cache

## Usage

**Platform prerequisites:** `make`, `docker`, `docker-compose`, `bash`

**Configuration:** 

Configuration can be set in the .env file

```
CAPACITY=100
GLOBAL_EXPIRY=3600
PORT=8080
REDIS_ADDRESS=redis:6379
MAX_CLIENTS=5
```

**Running:**

```bash
# clone the redisproxy git repo
git clone https://github.com/ashwathraop/redisproxy

# cd into the git repo
cd redisproxy

# Build and run tests
make test

# Just run in the docker containers
make run

# Stop the containers
make stop
```
 
**API:**

- `GET /` shows usage description.
- `GET /key` The value of `key` is returned from cache if available, or from backend redis. If the key is not stored, returns 404 error.

## High-level architecture overview.

There are three main parts to the redisproxy:

**1. LRUCache**

The cache is implemented as an LRU cache. Configuration options for the cache are:

- `CAPACITY`: The cache capacity is configured in terms of the number of keys it retains. On capacity, LRU eviction kicks in. 

- `GLOBAL_EXPIRY`: Global expiry in seconds, values added to the LRU cache are expired after being in the cache for a time duration that is set with GLOBAL_EXPIRY per instance. After a value expires, a GET request to the cache will act as if the key:value has never been stored in the cache.
  
**2. Backend Redis**

The backing redis instance associated to the proxy instance configurable with the configuration option:

- `REDIS_ADDRESS`: String value with "host:port" format. For example, `localhost:6379`.

**3. HTTP Server**

A basic HTTP server handling `GET` requests. A GET request to the endpoint `/key` will try to retrieve a value from the cache, and if not found, tries to fetch the value from backend redis. 


**Parallel concurrent access:** 
- `MAX_CLIENTS`: Number of requests is controlled by a simple solution of using a semaphore with value set to MAX_CLIENTS variable. HTTP server is running in a multi threaded mode and once requests exhaust sempahore value, an error with code 429 is returned.

**Redis client protocol Server**
- Implemented a very basic GET request handler with Redis Protocol specification which can return RESP Simple Strings. It can talk to Cache and backend redis server just like HTTP proxy, so cache expiry and LRU eviction works. This can be further improved to handle all datatypes supported by RESP.
## Code Overview

The code for redis proxy is split into five main files:

**utils.py**
- Utility code like argument parser is handled here.

**backredis.py**
- Connection to backend redis server and fetching data is handled in this file.

**cache.py**
- This file houses LRUcache implemetation. Includes initialization of OrderedDict and a mutex, which protects get and add operations to the cache.

**proxy.py**
- This is the main file for HTTP Proxy, starts the server in mutithreaded mode and also manages handling of HTTP request/responses.

**resp.py**
- This file starts a RESP compliant server and capable of serving simple redis GET operations.

## Algorithmic Complexity

**Cache Operations**

Overall cache operations take O(1) time. This is acheived by using Python's `collections.OrderedDict` library which internally uses HashMap and LinkedList and provides constant operation time for lookup, add, move_to_end() and del(). It takes O(2n) space to maintain Hastable and LinkedList. Additionally cache's key expiry check is a `O(1)` operation as well.

**Proxy Operations**

If the Cache has requested `key`, retrieve the value in `O(1)` time. If not, a GET request is made to backendredis, which is an `O(1)` operation considering all the data fits in memory, otherwise its `O(1+n/k)` where n is the number of items and k the number of buckets. Reference: https://stackoverflow.com/a/15218599

## Time spent on each part of the project.
- Docker setup: 30 mins
- Cache implementation: 45 mins
- Server implementation: 15 mins
- Multithreaded server: 30 mins
- Redis client protocol: 1 hour
- Test cases implementation: 1 hour
- Running tests: 30 mins
- Automated tests using Makefile: 15 mins
- README: 30 mins