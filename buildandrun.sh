#!/bin/bash

version=`git branch | grep '*' | grep -v master | cut -f 2 -d '-'`
running_version=`docker ps | grep chatserver | awk '{print $NF}' | cut -f 2 -d '-'`
if [ "X${version}" != "X" ] ; then
	if [ "X${version}" != "X${running_version}" ] ; then
		docker build --tag=chatserver:v${version} . -f dockerfiles/chatserver/Dockerfile
		if [ $? -eq 0 ] ; then
			if [ "X${running_version}" != "X" ] ; then
				docker stop chatserver-${running_version} 
			fi
			if [ $? -eq 0 ] ; then
				docker run -p 0.0.0.0:65533:65533 -dt --name=chatserver-${version} --restart=always chatserver:v${version} -v
			fi
		fi
		
	else
		echo "chatserver: Running version is already ${version}"
	fi
else
	echo "chatserver: No version information for chatserver"
fi


