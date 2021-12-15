# perfSONAR Testpoint

FROM debian:stretch

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y install -y \
        curl \
        gnupg

RUN curl -o /etc/apt/sources.list.d/perfsonar-release.list http://downloads.perfsonar.net/debian/perfsonar-release.list
RUN curl http://downloads.perfsonar.net/debian/perfsonar-official.gpg.key | apt-key add -

RUN apt-get update && \
    apt-get -y install \
        perfsonar-testpoint
