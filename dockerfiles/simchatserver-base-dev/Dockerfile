# Docker image for running python applications

FROM python:3.9-slim
MAINTAINER Matt Clark <mattjclark0407@hotmail.com>

COPY binaries/python36/* /tmp
COPY dockerfiles/simchatserver-base/pip.conf /etc/pip.conf
ENV PIP_CONFIG_FILE /etc/pip.conf
RUN pip install --no-cache pycryptodome requests simplejson cachetools python-memcached
RUN useradd sysadmin
WORKDIR /usr/local/src
RUN mkdir -p /usr/local/src/simchatserver
WORKDIR /usr/local/src/simchatserver
COPY . /usr/local/src/simchatserver/
RUN pip install --pre -r requirements.txt
RUN python setup.py install

