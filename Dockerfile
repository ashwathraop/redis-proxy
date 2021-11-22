FROM python:alpine3.14
LABEL maintainer="ashwath.ash@gmail.com"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV CAPACITY=1000
ENV GLOBAL_EXPIRY=3600
ENV PORT=8080
ENV REDIS_ADDRESS=redis:6379
ENV MAX_CLIENTS=5

COPY . /workspace/redis-proxy
WORKDIR /workspace/redis-proxy
EXPOSE 8080
CMD python3 ./src/proxy.py


