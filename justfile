build:
    uv tool run --with tox-uv tox -e build

docker-build:
    docker build \
        --progress=plain \
        --build-arg BASE_CONTAINER_VERSION=4.4.1 \
        --build-arg REGISTRY=docker.osdc.io/ncigdc \
        -t "dev-containers.osdc.io/ncigdc/fastqc_to_json:$(git rev-parse --short HEAD)" \
        .

clean: clean-dirs

clean-dirs:
    rm -rf ./build/
    rm -rf ./dist/
    rm -rf ./*.egg-info/
    rm -rf ./htmlcov/

detect-secrets: scan-secrets audit-secrets

scan-secrets:
    detect-secrets scan --baseline .secrets.baseline

audit-secrets:
    detect-secrets audit .secrets.baseline

init: init-hooks init-pip

init-hooks:
    pre-commit install

init-pip:
    uv pip install ".[dev,test]"

venv:
    rm -rf .venv/
    uv venv

compile-requirements:
    uv tool run --with tox-uv tox -e compile

tox:
    @echo
    TOX_PARALLEL_NO_SPINNER=1 uv tool run --with tox-uv tox -p --recreate

upload:
    uv tool run --with tox-uv tox -e publish

version:
    uv tool run --with tox-uv tox -e version
