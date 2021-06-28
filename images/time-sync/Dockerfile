FROM alpine:3.13

RUN apk add \
        chrony \
        gpsd \
        gpsd-clients \
        py3-pip

RUN pip3 install \
    kubernetes

COPY update_status.py /
