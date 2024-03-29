#!/bin/bash

version=0.1
container_name="testpoint01-erigrid20"
image="erigrid20/perfsonar-testpoint:${version}"
host_name="kojumaki-vtt"

if [ $# -lt 1 ]
then
   echo "Usage: $0 up|down|exec|build"
   exit
fi

dir=$1

if [ ${dir} = "up" ]
then
#    docker run --rm -d --network host --name ${container_name} -v $PWD/lsregistrationdaemon.conf:/usr/share/doc/perfsonar-lsregistrationdaemon/examples/lsregistrationdaemon.conf ${image}
    docker run --rm -d --hostname ${host_name} --name ${container_name} -v $PWD/erigrid.conf:/etc/perfsonar/psconfig/archives.d/erigrid.conf -v $PWD/lsregistrationdaemon.conf:/usr/share/doc/perfsonar-lsregistrationdaemon/examples/lsregistrationdaemon.conf ${image}
elif [ ${dir} = "down" ]
then
   docker stop ${container_name}
elif [ ${dir} = "exec" ]
then
   docker exec -it ${container_name} bash
elif [ ${dir} = "build" ]
then
   docker build -t ${image} -f Dockerfile .
else
   echo "Unknown command -> bailing out"
fi
