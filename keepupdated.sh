#!/bin/bash

while true; do
    if git pull | grep -q "simchatserver already up-to-date" ; then
        echo "`date`: simchatserver already up to date"
    else
        docker build . --tag=simchatserver:dev -f dockerfiles/simchatserver/Dockerfile && \
        docker stop simchatserver && \
        docker rm simchatserver && docker run -dt --restart=always --name=simchatserver simchatserver:dev -v
    fi
    echo "`date`: Sleeping for 60 seconds"
    sleep 60
done
