FROM alpine:3 AS codeclimate

ENV container docker

WORKDIR /work

COPY local/engine.json ./engine.json
COPY local/codeclimate-semgrep /usr/local/bin/

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]
RUN adduser --uid 9000 --gecos "" --disabled-password app \
  && apk --no-cache add --virtual build-deps \
  python3-dev~=3 \
  py3-pip~=20 \
  && apk --no-cache add --virtual cc-deps \
  bash~=5 \
  jq~=1 \
  && apk --no-cache add \
  python3~=3 \
  && pip3 install --no-cache-dir \
  "semgrep==*" \
  && find /usr/lib/ -name '__pycache__' -print0 | xargs -0 -n1 rm -rf \
  && find /usr/lib/ -name '*.pyc' -print0 | xargs -0 -n1 rm -rf \
  && VERSION="$(semgrep --version | 2>&1 | sed -n 3p)" \
  && jq --arg version "$VERSION" '.version = $version' > /engine.json < ./engine.json \
  && rm ./engine.json \
  && apk del build-deps

USER app

VOLUME /code
WORKDIR /code

CMD ["codeclimate-semgrep"]

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

FROM codeclimate AS semgrep

WORKDIR /work

USER root

RUN apk del cc-deps \
  && rm /engine.json /usr/local/bin/codeclimate-semgrep

ENTRYPOINT ["semgrep"]
CMD ["--version"]

LABEL space.megabyte.type="linter"
