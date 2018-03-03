# Docker image for running python applications

FROM python:2-slim
MAINTAINER Matt Clark <mattjclark0407@hotmail.com>

RUN useradd sysadmin
WORKDIR /usr/local/src
RUN mkdir -p /usr/local/src/simchatserver
WORKDIR /usr/local/src/simchatserver
COPY . /usr/local/src/simchatserver/
RUN python setup.py install
USER sysadmin
EXPOSE 65533
ENTRYPOINT ["simchatserver"]
