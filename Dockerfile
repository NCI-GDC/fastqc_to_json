ARG REGISTRY=docker.osdc.io/ncigdc
ARG BASE_CONTAINER_VERSION=4.4.1

FROM ${REGISTRY}/amzn2023-builder:${BASE_CONTAINER_VERSION} AS builder

ENV UV_PYTHON=3.11

COPY ./ /fastqc_to_json

WORKDIR /fastqc_to_json

# Build the wheel through the existing tox build environment,
# but use uv/tox-uv instead of installing tox with pip.
RUN uv tool run --with tox-uv tox -e build


FROM ${REGISTRY}/amzn2023-builder:${BASE_CONTAINER_VERSION}

LABEL org.opencontainers.image.title="fastqc_to_json" \
      org.opencontainers.image.description="fastqc_to_json" \
      org.opencontainers.image.source="https://github.com/NCI-GDC/fastqc_to_json" \
      org.opencontainers.image.vendor="NCI GDC"

ENV UV_PYTHON=3.11

COPY --from=builder /fastqc_to_json/dist/*.whl /fastqc_to_json/

WORKDIR /fastqc_to_json

# Create the runtime venv and install the built wheel.
RUN uv venv .venv && \
    uv pip install --python .venv/bin/python --no-deps *.whl && \
    rm -f *.whl

ENV PATH="/fastqc_to_json/.venv/bin:$PATH"

USER app

ENTRYPOINT ["fastqc_to_json"]

CMD ["--help"]
