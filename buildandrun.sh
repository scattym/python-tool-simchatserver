#!/bin/bash

version=`git branch | grep '*' | grep -v master | cut -f 2 -d '-'`
version=`git describe --tags --dirty`
running_version=`docker ps | grep simchatserver | awk '{print $NF}' | cut -f 2 -d '-'`
echo "Version is ${version}"
echo "Running version is ${running_version}"
if [ "X${version}" != "X" ] ; then
	if [ "X${version}" != "X${running_version}" ] ; then
	    docker run -dt -p 5672:5672 --restart=always --name=rabbitmq rabbitmq:3.7
	    docker build --tag=simchatserver-base:interim . -f dockerfiles/simchatserver-base/Dockerfile
		docker build --tag=simchatserver:v${version} . -f dockerfiles/simchatserver/Dockerfile
		docker build --tag=mqrecv-cell-update:v${version} . -f dockerfiles/mqrecv-cell-update/Dockerfile
        docker build --tag=mqrecv-event:v${version} . -f dockerfiles/mqrecv-event/Dockerfile
        docker build --tag=mqrecv-gps-update:v${version} . -f dockerfiles/mqrecv-gps-update/Dockerfile
        docker build --tag=mqrecv-firmware-update:v${version} . -f dockerfiles/mqrecv-firmware-update/Dockerfile
        docker build --tag=mqrecv-mt-file:v${version} . -f dockerfiles/mqrecv-mt-file/Dockerfile
        docker build --tag=meitrackbot:v${version} . -f dockerfiles/meitrackbot/Dockerfile


		if [ $? -eq 0 ] ; then
			if [ "X${running_version}" != "X" ] ; then
				docker stop simchatserver-${running_version}
				docker stop mqrecv-cell-update-${running_version}
				docker stop mqrecv-event-${running_version}
				docker stop mqrecv-gps-update-${running_version}
				docker stop mqrecv-firmware-update-${running_version}
				docker stop mqrecv-mt-file-${running_version}
				docker stop meitrackbot-${running_version}

			fi
			if [ $? -eq 0 ] ; then
				docker run -p 0.0.0.0:65533:65533 -dt --name=simchatserver-${version} --restart=always simchatserver:v${version} -v
				docker run -dt --name=mqrecv-cell-update-${running_version} --restart=always mqrecv-cell-update:v${version} -v
				docker run -dt --name=mqrecv-event-${running_version} --restart=always mqrecv-event:v${version} -v
				docker run -dt --name=mqrecv-gps-update-${running_version} --restart=always mqrecv-gps-update:v${version} -v
				docker run -dt --name=mqrecv-firmware-update-${running_version} --restart=always mqrecv-firmware-update:v${version} -v
				docker run -dt --name=mqrecv-mt-file-${running_version} --restart=always mqrecv-mt-file:v${version} -v
				docker run -dt --name=meitrackbot-${running_version} --restart=always meitrackbot:v${version} -v
			fi
		fi
		
	else
		echo "simchatserver: Running version is already ${version}"
	fi
else
	echo "simchatserver: No version information for simchatserver"
fi


