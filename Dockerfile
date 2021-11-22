FROM python:alpine3.14
LABEL maintainer="ashwath.ash@gmail.com"

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /workspace/redis-proxy
WORKDIR /workspace/redis-proxy
EXPOSE 8080
CMD python3 ./src/proxy.py