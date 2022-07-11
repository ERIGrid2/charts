#!/bin/bash

# https://www.docker.com/blog/containerize-your-go-developer-environment-part-1/

REGISTRY=erigrid

PLATFORMS=linux/arm/v7,linux/arm64,linux/amd64

if (( $# >= 1)); then
	IMAGES=$@
else
	IMAGES="time-sync perfsonar-testpoint netem"
fi

function docker_init_buildkit() {
	docker buildx create --platform linux/arm/v7,linux/arm64,linux/amd64 --use --driver docker-container --name riasc

	# Setup qemu-static emulation
	docker run --rm --privileged aptman/qus -s -- -p
	export DOCKER_BUILDKIT=1
}

function docker_build() {
	if ! [ -d $1 ]; then
		echo -e "Directory does not exist: $1"
		exit -1
	fi

	docker buildx build \
		--builder riasc \
		--platform ${PLATFORMS} \
		--tag ${REGISTRY}/$1 \
		--push $1
}

docker_init_buildkit

for IMAGE in ${IMAGES}; do
	docker_build ${IMAGE}
done
