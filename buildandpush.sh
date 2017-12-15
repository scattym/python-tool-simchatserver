#!/bin/bash

version=`git branch | grep '*' | grep -v master | cut -f 2 -d '-'`
if [ "X${version}" != "X" ] ; then
	docker build --tag=gcr.io/geotool-test/simchatserver:v${version} . -f dockerfiles/simchatserver/Dockerfile
	if [ $? -eq 0 ] ; then
		gcloud docker -- push gcr.io/geotool-test/simchatserver:v${version}
	fi
else
	echo "simchatserver: No version information for nmeaproxy"
fi
