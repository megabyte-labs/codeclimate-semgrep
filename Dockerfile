FROM ubuntu:20.04 AS base

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
    'curl=7.*' \
    'nodejs=10.*' \
    'npm=6.*' \
    'git=1:2.*' \
    'build-essential=*' \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /usr/local/bin/hadolint https://github.com/hadolint/hadolint/releases/download/v1.19.0/hadolint-Linux-x86_64 && chmod +x /usr/local/bin/hadolint

RUN pip3 install 'poetry>=0.12' && poetry config virtualenvs.in-project true

RUN npm install -g quicktype@"15.x"

WORKDIR /workspaces/codeclimate-semgrep

FROM development AS build

COPY . .
RUN make build-package

FROM base AS release

COPY engine.json /engine.json
COPY --from=build /workspaces/codeclimate-semgrep/dist /tmp/dist

RUN pip3 install /tmp/dist/*.whl && rm -rf /tmp/dist /root/.cache/pip

RUN useradd -u 9000 -M app
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
LABEL org.opencontainers.image.description="Code Climate engine for Semgrep"
LABEL org.opencontainers.image.documentation="https://gitlab.com/megabyte-labs/docker/codeclimate/semgrep/-/blob/master/README.md"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.revision=$REVISION
LABEL org.opencontainers.image.source="https://gitlab.com/megabyte-labs/docker/codeclimate/semgrep.git"
LABEL org.opencontainers.image.url="https://megabyte.space"
LABEL org.opencontainers.image.vendor="Megabyte Labs"
LABEL org.opencontainers.image.version=$VERSION
LABEL space.megabyte.type="code-climate"