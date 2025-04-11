ARG REGISTRY=docker.osdc.io/ncigdc
ARG BASE_CONTAINER_VERSION=latest

FROM ${REGISTRY}/python3.9-builder:${BASE_CONTAINER_VERSION} as builder

# Install necessary build dependencies including clang
RUN dnf update --refresh -y && \
    dnf install -y clang boost boost-devel gcc-c++ git make

COPY ./ /fastqc_to_json

WORKDIR /fastqc_to_json

RUN pip install tox && tox -e build

FROM ${REGISTRY}/python3.9:${BASE_CONTAINER_VERSION}

LABEL org.opencontainers.image.title="fastqc_to_json" \
      org.opencontainers.image.description="fastqc_to_json" \
      org.opencontainers.image.source="https://github.com/NCI-GDC/fastqc_to_json" \
      org.opencontainers.image.vendor="NCI GDC"

COPY --from=builder /fastqc_to_json/dist/*.whl /fastqc_to_json/
COPY requirements.txt /fastqc_to_json/

WORKDIR /fastqc_to_json

RUN pip install --no-deps -r requirements.txt \
	&& pip install --no-deps *.whl \
	&& rm -f *.whl requirements.txt

USER app

ENTRYPOINT ["fastqc_to_json"]

CMD ["--help"]
