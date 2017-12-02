#!/bin/bash

version=`git branch | grep '*' | grep -v master | cut -f 2 -d '-'`
running_version=`docker ps | grep simchatserver | awk '{print $NF}' | cut -f 2 -d '-'`
if [ "X${version}" != "X" ] ; then
	if [ "X${version}" != "X${running_version}" ] ; then
		docker build --tag=simchatserver:v${version} . -f dockerfiles/simchatserver/Dockerfile
		if [ $? -eq 0 ] ; then
			if [ "X${running_version}" != "X" ] ; then
				docker stop simchatserver-${running_version}
			fi
			if [ $? -eq 0 ] ; then
				docker run -p 0.0.0.0:65533:65533 -dt --name=simchatserver-${version} --restart=always simchatserver:v${version} -v
			fi
		fi
		
	else
		echo "simchatserver: Running version is already ${version}"
	fi
else
	echo "simchatserver: No version information for simchatserver"
fi


