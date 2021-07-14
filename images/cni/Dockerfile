ARG ARCH=amd64
ARG VERSION=v0.9.1

FROM debian:buster

ADD https://github.com/containernetworking/plugins/releases/download/$(VERSION)/cni-plugins-linux-$(ARCH)-$(VERSION).tgz /cni

ADD entrypoint.sh /

CMD ["/entrypoint.sh"]
