#!/bin/bash

while true; do
    if git pull | grep -q "Already up-to-date" ; then
        echo "`date`: Already up to date"
    else
        docker build . --tag=nmeaproxy:dev -f Dockerfile-dev && \
        docker stop nmeaproxy && \
        docker rm nmeaproxy && docker run -dt --restart=always --name=nmeaproxy -e GEO_API_HOST=localhost:8001 -p 65535:5000 nmeaproxy:dev -x -s geotool.scattym.com:8001 -t -x
    fi
    echo "`date`: Sleeping for 60 seconds"
    sleep 60
done
