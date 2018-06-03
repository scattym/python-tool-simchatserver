# Docker image for running python applications

FROM simchatserver-base:interim
MAINTAINER Matt Clark <mattjclark0407@hotmail.com>

USER sysadmin

RUN pip install celery
ENTRYPOINT ["/usr/local/bin/celery"]
CMD ["-A", "sim_chat_lib.celerytasks.sendcommand", "worker", "-l", "info"]
