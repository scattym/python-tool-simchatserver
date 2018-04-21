#!/bin/bash

version=`git branch | grep '*' | grep -v master | cut -f 2 -d '-'`
if [ "X${version}" != "X" ] ; then
	docker build --tag=gcr.io/geotool-test/rabbitmq-mqtt:v${version} .
	if [ $? -eq 0 ] ; then
		gcloud docker -- push gcr.io/geotool-test/rabbitmq-mqtt:v${version}
		docker tag gcr.io/geotool-test/rabbitmq-mqtt:v${version} gcr.io/position-live/rabbitmq-mqtt:v${version}
		gcloud docker -- push gcr.io/position-live/rabbitmq-mqtt:v${version}
	fi
else
	echo "rabbitmq: No version information for rabbitmq image"
fi
