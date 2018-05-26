#!/bin/bash

CONTAINERS="mqrecv-cell-update mqrecv-event mqrecv-gps-update mqrecv-firmware-update mqrecv-mt-file"

while true; do
    if git pull | grep -q "Already up-to-date" ; then
        echo "`date`: simchatserver already up to date"
    else
        docker run -dt -p 5672:5672 --restart=always --name=rabbitmq rabbitmq:3.7
        docker build --tag=simchatserver-base:interim . -f dockerfiles/simchatserver-base-dev/Dockerfile

        for con in ${CONTAINERS} ; do
            docker build --tag=${con} . -f dockerfiles/${con}/Dockerfile
            docker stop ${con}
            docker rm ${con}
            docker run -dt --restart=always -e GEO_API_HOST=10.1.1.4:8000 -e MQ_HOST=10.1.1.4 -e DBHOST=10.1.1.4 -e DB_POOL_MAX=10 -e DB_POOL_MIN=1 --name=${con} ${con} -vvv
        done

        docker build . --tag=simchatserver -f dockerfiles/simchatserver/Dockerfile
        docker stop simchatserver
        docker rm simchatserver
        docker run -dt --restart=always --name=simchatserver -e MQ_HOST=10.1.1.4 -p 65533:65533 simchatserver -vv -s 10.1.1.4:8000
        docker ps -a | grep "xited" | awk '{print $1}' | xargs docker rm
        docker images | grep none | awk '{print $3}' | xargs docker rmi
    fi
    echo "`date`: Sleeping for 60 seconds"
    sleep 60
done
