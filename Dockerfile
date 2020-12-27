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
