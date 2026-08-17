ARG REGISTRY=docker.osdc.io/ncigdc
ARG BASE_CONTAINER_VERSION=4.4.1

FROM ${REGISTRY}/amzn2023-builder:${BASE_CONTAINER_VERSION}

ENV UV_PYTHON=3.11

USER app

WORKDIR /app
ENV UV_CACHE_DIR=/app/.cache/uv

RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --no-dev --active --no-binary

COPY . /app

RUN uv sync --no-dev --active --no-binary

LABEL org.opencontainers.image.title="fastqc_to_json" \
      org.opencontainers.image.description="fastqc_to_json" \
      org.opencontainers.image.source="https://github.com/NCI-GDC/fastqc_to_json" \
      org.opencontainers.image.vendor="NCI GDC"

ENV PATH="/app/.venv/bin:$PATH"

RUN fastqc_to_json --help

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD ["fastqc_to_json", "--help"]
