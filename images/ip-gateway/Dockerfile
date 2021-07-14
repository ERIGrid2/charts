FROM debian:buster

RUN apt-get update -qq && \
    apt-get install -qq \
        iproute2 \
        python3

ADD entrypoint.py /

CMD ["python3", "/entrypoint.py"]
