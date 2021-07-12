FROM debian:buster

RUN apt-get update && \
    apt-get -y install \
        chrony \
        gpsd \
        gpsd-clients \
        python3-pip

RUN pip3 install \
    kubernetes

COPY update_status.py /
