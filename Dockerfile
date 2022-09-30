FROM ubuntu:20.04 AS base

WORKDIR /work

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    'python3=3.8.*' \
    'python3-pip=20.*' \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base AS development

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl=7.* \
    jq=1.* \
    nodejs=10.* \
    npm=6.* \
    git=1:2.* \
    build-essential=* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install \
    poetry>=0.12 \
    && poetry config virtualenvs.in-project true \
    && npm install -g \
    quicktype@15.x

FROM development AS build

COPY local/codeclimate-semgrep .

RUN make build-package

FROM base AS codeclimate

COPY local/engine.json /engine.json
COPY --from=build /work/dist /tmp/dist

RUN pip3 install /tmp/dist/*.whl \
    && VERSION="$(semgrep --version 2>&1 | sed -n 3p)" \
    && jq --arg version "$VERSION" '.version = $version' > /engine.json < ./engine.json \
    && rm -rf /tmp/dist /root/.cache/pip \
    && useradd -u 9000 -M app

USER app

VOLUME /code
WORKDIR /code

CMD ["ccsemgrep"]

ARG BUILD_DATE
ARG REVISION
ARG VERSION

LABEL maintainer="Megabyte Labs <help@megabyte.space>"
LABEL org.opencontainers.image.authors="Brian Zalewski <brian@megabyte.space>"
LABEL org.opencontainers.image.created=$BUILD_DATE
LABEL org.opencontainers.image.description="A Semgrep slim container and a CodeClimate engine container for GitLab CI"
LABEL org.opencontainers.image.documentation="https://github.com/megabyte-labs/codeclimate-semgrep/blob/master/README.md"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.revision=$REVISION
LABEL org.opencontainers.image.source="https://github.com/megabyte-labs/codeclimate-semgrep.git"
LABEL org.opencontainers.image.url="https://megabyte.space"
LABEL org.opencontainers.image.vendor="Megabyte Labs"
LABEL org.opencontainers.image.version=$VERSION
LABEL space.megabyte.type="codeclimate"

FROM base AS semgrep

USER root

RUN python3 -m pip install semgrep

ENTRYPOINT ["semgrep"]
CMD ["--version"]

LABEL space.megabyte.type="linter"
