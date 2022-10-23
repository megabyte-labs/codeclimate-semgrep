FROM ubuntu:20.04 AS codeclimate-base

ENV DEBIAN_FRONTEND noninteractive
ENV container docker

WORKDIR /work

RUN useradd -u 9000 -M app \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    curl=7.* \
    jq=1.* \
    python3=3.8.* \
    python3-pip=20.* \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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

FROM codeclimate-base AS development

COPY local/engine.json ./engine.json

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  ca-certificates=* \
  curl=7.* \
  build-essential=* \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && pip3 install --no-cache-dir \
  semgrep==0.* \
  && find /usr/lib/ -name '__pycache__' -print0 | xargs -0 -n1 rm -rf \
  && find /usr/lib/ -name '*.pyc' -print0 | xargs -0 -n1 rm -rf \
  && VERSION="$(semgrep --version | 2>&1 | sed -n 3p)" \
  && jq --arg version "$VERSION" '.version = $version' > /engine.json < ./engine.json \
  && rm ./engine.json

FROM codeclimate-base AS codeclimate

COPY --from=development /usr/local/lib/python3.8/dist-packages /usr/local/lib/python3.8/dist-packages
COPY --from=development /usr/local/bin/semgrep /usr/local/bin/semgrep
COPY --from=development /engine.json /engine.json
COPY local/codeclimate-semgrep /usr/local/bin/

RUN chmod +x /usr/local/bin/codeclimate-semgrep \
  && mkdir -p /home/app \
  && chown -Rf app:app /home/app \
  && rm -rf /root/.semgrep

USER app

VOLUME /code
WORKDIR /code

CMD ["codeclimate-semgrep"]

FROM development AS semgrep

WORKDIR /work

USER root

RUN rm -rf /root/.semgrep

ENTRYPOINT ["semgrep"]
CMD ["--version"]

LABEL space.megabyte.type="linter"
