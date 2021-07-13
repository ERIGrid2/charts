# Make sure this is in sync with the multus-cni submodule
ARG COMMIT="9b45d4b211728aa0db44a1624aac8e61843390cf"
ARG VERSION="v3.7.2"

FROM --platform=${BUILDPLATFORM} golang:1.15.7-buster AS builder

ADD multus-cni /usr/src/multus-cni

WORKDIR /usr/src/multus-cni

ENV COMMIT=$(COMMIT)
ENV VERSION=$(VERSION)
RUN hack/build-go.sh

FROM debian:buster

WORKDIR /
COPY --from=builder /usr/src/multus-cni /usr/src/multus-cni
COPY --from=builder /usr/src/multus-cni/images/entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
