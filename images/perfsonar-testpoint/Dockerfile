# perfSONAR Testpoint

FROM debian:buster-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get -y --no-install-recommends install -y \
        curl \
        gnupg \
        postgresql postgresql-client \
        supervisor \
        rsyslog

RUN curl -o /etc/apt/sources.list.d/perfsonar-release.list http://downloads.perfsonar.net/debian/perfsonar-release.list
RUN curl http://downloads.perfsonar.net/debian/perfsonar-official.gpg.key | apt-key add -

# -----------------------------------------------------------------------

#
# PostgreSQL Server
#
# Based on a Dockerfile at
# https://raw.githubusercontent.com/zokeber/docker-postgresql/master/Dockerfile

# Postgresql version
ENV PG_VERSION=11
ENV PGVERSION=11

# Set the environment variables
ENV PGDATA=/var/lib/postgresql/$PG_VERSION/main

# Overlay the configuration files
COPY postgresql/postgresql.conf.debian_buster /etc/postgresql/$PG_VERSION/main/postgresql.conf
COPY postgresql/pg_hba.conf.debian_buster /etc/postgresql/$PG_VERSION/main/pg_hba.conf

#Start postgresql
RUN /etc/init.d/postgresql start

# End PostgreSQL Setup
# -----------------------------------------------------------------------------

# HACK
RUN mkdir -p /usr/share/doc/perfsonar-lsregistrationdaemon/examples/ /usr/share/doc/perfsonar-testpoint/
COPY lsregistrationdaemon.conf /usr/share/doc/perfsonar-lsregistrationdaemon/examples/lsregistrationdaemon.conf
COPY changelog.gz /usr/share/doc/perfsonar-testpoint/changelog.gz
# HACK ends

# Rsyslog
COPY rsyslog/python-pscheduler.conf /etc/rsyslog.d/python-pscheduler.conf
COPY rsyslog/owamp-syslog.conf /etc/rsyslog.d/owamp-syslog.conf

# Install perfsonar-testpoint package
RUN apt-get update && \
    apt-get -y --no-install-recommends install \
        perfsonar-testpoint

# clean package cache
RUN apt clean; rm -rf /var/cache/apt/archives

# The following ports are used:
# pScheduler: 443
# owamp:861, 8760-9960
# twamp: 862, 18760-19960
# simplestream: 5890-5900
# nuttcp: 5000, 5101
# iperf2: 5001
# iperf3: 5201
EXPOSE 443 861 862 5000-5001 5101 5201 8760-9960 18760-19960

# add pid directory, logging, and postgres directory
VOLUME ["/var/run", "/var/lib/postgresql", "/var/log", "/etc/rsyslog.d" ]

RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisord.conf
COPY initialise.sh /etc/init.d/initialise.sh

CMD /usr/bin/supervisord -c /etc/supervisord.conf
