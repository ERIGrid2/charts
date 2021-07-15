FROM debian:buster

RUN apt-get update && \
    apt-get -y install \
        chrony \
        gpsd \
        gpsd-clients \
        python3-pip \
        linuxptp \
        ethtool

RUN pip3 install \
    kubernetes

COPY chrony-monitor.py /

CMD ["python3", "/chrony-monitor.py"]
