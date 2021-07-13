FROM debian:buster

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-dev \
        python3-pip \
        git

RUN pip3 install git+https://github.com/erigrid2/k8s-netem@30462eaddc0bb4e5555434c1977295f26f689c43

CMD ["k8s-netem"]
