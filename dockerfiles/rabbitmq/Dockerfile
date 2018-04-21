# Docker image for running rabbit mq with mqtt applications

FROM rabbitmq:3.7
MAINTAINER Matt Clark <mattjclark0407@hotmail.com>

RUN rabbitmq-plugins enable rabbitmq_management
RUN rabbitmq-plugins enable rabbitmq_mqtt

ADD entrypoint.sh /entrypoint.sh
ADD rabbitmq.conf /etc/rabbitmq/rabbitmq.conf
RUN chmod +x /entrypoint.sh
EXPOSE 15672
EXPOSE 65532

# Define default command
CMD ["/entrypoint.sh"]
