FROM debian:buster AS builder

RUN apt-get update && \
	apt-get -y install \
		build-essential \
		git \
		autotools-dev \
		automake \
		texinfo

RUN git clone https://github.com/HewlettPackard/netperf.git && \
	cd netperf && \
	./autogen.sh && ./configure --enable-demo && \
	make install

FROM debian:buster

RUN apt-get update && \
	apt-get -y install \
		irtt \
		iputils-ping \
		fping \
		iperf \
		python3-pip \
		git

COPY --from=builder /usr/local/ /usr/local/

ENV PATH=/usr/local/bin:${PATH}

RUN pip3 install \
	flent \
	matplotlib \
	git+https://github.com/ERIGrid2/k8s-flent.git
