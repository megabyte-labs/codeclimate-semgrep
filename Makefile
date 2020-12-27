ifeq ($(origin TAG), undefined)
	TAG := $(shell date +"local-%Y-%m-%d_%H-%M-%S")
endif

REPO          := codeclimate/codeclimate-semgrep
BUILD_CONTEXT := $(abspath .)
TARGET        := development
HOST_SRC      := ${BUILD_CONTEXT}
CONTAINER_SRC := /workspaces/codeclimate-semgrep

MODULE_DIR    := codeclimate_semgrep
SCHEMA_DIR    := schemas
JSON_SCHEMAS  := $(shell find $(SCHEMA_DIR) -name '*.json')
PY_SCHEMAS    := $(patsubst $(SCHEMA_DIR)/%.json,$(MODULE_DIR)/%.py,$(JSON_SCHEMAS))


.PHONY: test
test:
	poetry run pytest

.PHONY: lint-all
lint-all: lint-dockerfile lint-python

.PHONY: lint-dockerfile
lint-dockerfile:
	hadolint Dockerfile

.PHONY: lint-python
lint-python:
	poetry run pylint codeclimate_semgrep
	poetry run mypy codeclimate_semgrep

.PHONY: build-docker
build-docker:
	docker build --target ${TARGET} -t ${REPO}:${TAG} ${BUILD_CONTEXT}
	@echo "----"
	@echo "To run a shell: TAG=${TAG} make shell"

.PHONY: build-package
build-package:
	poetry build -n -f wheel

.PHONY: shell
shell:
	docker run -it --entrypoint /bin/bash \
		-v ${HOST_SRC}:${CONTAINER_SRC} \
		${REPO}:${TAG}

.PHONY: all-schemas
all-schemas: $(PY_SCHEMAS)

$(MODULE_DIR)/%.py: schemas/%.json
	@mkdir -p "$(@D)"
	echo "# pylint: skip-file" > "$@"
	quicktype -l py -s schema --python-version 3.7 --src "$<" --top-level "$(notdir $*)" >> "$@"
	python3 -c 'import sys, json, pprint; out = "\nSCHEMA = %s" % pprint.pformat(json.load(open(sys.argv[1]))); print(out)' "$<" >> "$@"

.PHONY: codeclimate-analyze
codeclimate-analyze:
	cd tests && CODECLIMATE_DEBUG=1 codeclimate analyze --dev

.PHONY: test-container
test-container:
	docker run \
		-v "${BUILD_CONTEXT}/tests/config.json:/config.json" \
		-v "${BUILD_CONTEXT}/tests:/code" \
		${REPO}:${TAG}

.PHONY: test-run
test-run:
	poetry run ccsemgrep -d tests -c tests/config.json

.PHONY: clean
clean:
	rm -f $(PY_SCHEMAS)
	rm -rf dist/*
