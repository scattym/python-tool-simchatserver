#!/bin/bash

while true; do
    if git pull | grep -q "Already up-to-date" ; then
        echo "`date`: simchatserver already up to date"
    else
        docker build . --tag=simchatserver -f dockerfiles/simchatserver/Dockerfile && \
        docker stop simchatserver && \
        docker rm simchatserver && docker run -dt --restart=always --name=simchatserver -p 65533:65533 simchatserver -v -s 10.1.1.4:8000
        docker images | grep none | awk '{print $3}' | xargs docker rmi
    fi
    echo "`date`: Sleeping for 60 seconds"
    sleep 60
done
