# Docker image for running python applications

FROM python:3.6-slim
MAINTAINER Matt Clark <mattjclark0407@hotmail.com>

COPY binaries/python36/* /tmp
RUN pip install --no-cache --use-wheel /tmp/pycrypto-2.6.1-cp36-cp36m-linux_x86_64.whl
RUN pip install --no-cache requests
RUN pip install --no-cache simplejson
RUN pip install --no-cache cachetools
RUN pip install --no-cache python-memcached
RUN useradd sysadmin
WORKDIR /usr/local/src
RUN mkdir -p /usr/local/src/simchatserver
WORKDIR /usr/local/src/simchatserver
COPY . /usr/local/src/simchatserver/
RUN python setup.py install
USER sysadmin
ENTRYPOINT ["mqtt_receiver"]
