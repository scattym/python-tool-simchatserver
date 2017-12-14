# Docker image for running python applications

FROM python:2.7-slim
MAINTAINER Matt Clark <mattjclark0407@hotmail.com>

RUN useradd sysadmin
WORKDIR /usr/local/bin
COPY scripts/simchatserver /usr/local/bin/
RUN chown sysadmin:sysadmin /usr/local/bin/simchatserver
USER sysadmin
EXPOSE 65533
ENTRYPOINT ["/usr/local/bin/simchatserver"]
