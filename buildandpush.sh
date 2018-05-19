#!/bin/bash

#version=`git branch | grep '*' | grep -v master | cut -f 2 -d '-'`
version=`git describe --tags --dirty`
if [ "X${version}" != "X" ] ; then
    docker build --tag=simchatserver-base:interim . -f dockerfiles/simchatserver-base/Dockerfile

    docker build --tag=gcr.io/geotool-test/simchatserver:v${version} . -f dockerfiles/simchatserver/Dockerfile
    docker build --tag=gcr.io/geotool-test/mqrecv-cell-update:v${version} . -f dockerfiles/mqrecv-cell-update/Dockerfile
    docker build --tag=gcr.io/geotool-test/mqrecv-event:v${version} . -f dockerfiles/mqrecv-event/Dockerfile
    docker build --tag=gcr.io/geotool-test/mqrecv-gps-update:v${version} . -f dockerfiles/mqrecv-gps-update/Dockerfile
    docker build --tag=gcr.io/geotool-test/mqrecv-firmware-update:v${version} . -f dockerfiles/mqrecv-firmware-update/Dockerfile

    if [ $? -eq 0 ] ; then
        gcloud docker -- push gcr.io/geotool-test/simchatserver:v${version}
        gcloud docker -- push gcr.io/geotool-test/mqrecv-cell-update:v${version}
        gcloud docker -- push gcr.io/geotool-test/mqrecv-event:v${version}
        gcloud docker -- push gcr.io/geotool-test/mqrecv-gps-update:v${version}
        gcloud docker -- push gcr.io/geotool-test/mqrecv-firmware-update:v${version}
        docker tag gcr.io/geotool-test/simchatserver:v${version} gcr.io/position-live/simchatserver:v${version}
        docker tag gcr.io/geotool-test/mqrecv-cell-update:v${version} gcr.io/position-live/mqrecv-cell-update:v${version}
        docker tag gcr.io/geotool-test/mqrecv-event:v${version} gcr.io/position-live/mqrecv-event:v${version}
        docker tag gcr.io/geotool-test/mqrecv-gps-update:v${version} gcr.io/position-live/mqrecv-gps-update:v${version}
        docker tag gcr.io/geotool-test/mqrecv-firmware-update:v${version} gcr.io/position-live/mqrecv-firmware-update:v${version}
        gcloud docker -- push gcr.io/position-live/simchatserver:v${version}
        gcloud docker -- push gcr.io/position-live/mqrecv-cell-update:v${version}
        gcloud docker -- push gcr.io/position-live/mqrecv-event:v${version}
        gcloud docker -- push gcr.io/position-live/mqrecv-gps-update:v${version}
        gcloud docker -- push gcr.io/position-live/mqrecv-firmware-update:v${version}

    fi
else
    echo "simchatserver: No version information for nmeaproxy"
fi
