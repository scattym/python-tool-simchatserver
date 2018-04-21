#!/bin/sh

# Create Rabbitmq user
( sleep 10 ; \
rabbitmqctl add_user test apw4mqtt2u; \
rabbitmqctl set_permissions -p / test ".*" ".*" ".*"; \
rabbitmqctl add_user sysadmin apw4sysadmin2u ; \
rabbitmqctl set_user_tags sysadmin administrator ; \
rabbitmqctl set_permissions -p / sysadmin ".*" ".*" ".*"; \
echo "*** Log in the WebUI at port 15672 (example: http:/localhost:15672) ***") &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
rabbitmq-server $@