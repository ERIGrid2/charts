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

RUN mkdir -p /var/log/supervisor 
ADD supervisord.conf /etc/supervisord.conf

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
VOLUME ["/var/run", "/var/lib/pgsql", "/var/log", "/etc/rsyslog.d" ]

CMD /usr/bin/supervisord -c /etc/supervisord.conf
