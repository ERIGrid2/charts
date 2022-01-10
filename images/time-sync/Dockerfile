FROM debian:buster

RUN apt-get update && \
    apt-get -y install \
        chrony \
        gpsd \
        gpsd-clients \
        python3-pip \
        linuxptp \
        ethtool

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY status.py /

CMD ["python3", "/status.py"]
