FROM centos:8
MAINTAINER Ashwath Rao <ashwath.ash@gmail.com>
LABEL maintainer="ashwath.ash@gmail.com"
USER 0
RUN dnf -y install python3 redis
RUN pip3 install redis
COPY . /workspace
STOPSIGNAL SIGRTMIN+3
