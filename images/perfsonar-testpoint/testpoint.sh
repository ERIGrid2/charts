#!/bin/bash

version=0.1
name="testpoint01-erigrid20"
image="erigrid20/perfsonar-testpoint:${version}"

if [ $# -lt 1 ]
then
   echo "Usage: $0 up|down|exec|build"
   exit
fi

dir=$1

if [ ${dir} = "up" ]
then
#    docker run --rm -d --network host --name ${name} -v $PWD/lsregistrationdaemon.conf:/usr/share/doc/perfsonar-lsregistrationdaemon/examples/lsregistrationdaemon.conf ${image}
    docker run --rm -d --name ${name} -v $PWD/lsregistrationdaemon.conf:/usr/share/doc/perfsonar-lsregistrationdaemon/examples/lsregistrationdaemon.conf ${image}
elif [ ${dir} = "down" ]
then
   docker stop ${name}
elif [ ${dir} = "exec" ]
then
   docker exec -it ${name} bash
elif [ ${dir} = "build" ]
then
   docker build -t ${image} -f Dockerfile .
else
   echo "Unknown command -> bailing out"
fi
