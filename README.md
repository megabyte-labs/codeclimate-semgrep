# codeclimate-semgrep

A [Code Climate analysis engine](https://docs.codeclimate.com/docs/building-a-code-climate-engine)
for running [Semgrep](https://semgrep.dev) against your code.

## Description

This engine is used to run Semgrep rules against your code, allowing for custom
static analysis on multiple languages. Due to licensing it doesn't ship with the
[community-created Semgrep rules](https://github.com/returntocorp/semgrep-rules),
but you're free to use these in your own project.

## Getting Started

The engine itself is written in Python and wrapped up in a Docker container. To
build the container:

```
$ make build-docker TAG=latest TARGET=release
```

You can then test it using the `--dev` flag to the Code Climate CLI, e.g.

```
$ cat .codeclimate.yml
version: "2"
plugins:
  semgrep:
    enabled: true
    runs:
      - configs: ["rules/lang/correctness"]
$ codeclimate analyze --dev -f html > /tmp/out.html
```

To test or develop the engine, you can build the container to its `development`
target and bring up a shell:

```
$ make build-docker
# ...
Successfully built b7abc7867ea3
Successfully tagged codeclimate/codeclimate-semgrep:local-2020-12-26_21-50-16
----
To run a shell: TAG=local-2020-12-26_21-50-16 make shell
$ TAG=local-2020-12-26_21-50-16 make shell
docker run -it --entrypoint /bin/bash \
		-v /Users/ggironda/Repositories/codeclimate-semgrep:/workspaces/codeclimate-semgrep \
		codeclimate/codeclimate-semgrep:local-2020-12-26_21-50-16
root@5db0b146007b:/workspaces/codeclimate-semgrep# make test
poetry run pytest
============================================================================================= test session starts ==============================================================================================
platform linux -- Python 3.8.5, pytest-5.4.3, py-1.10.0, pluggy-0.13.1
rootdir: /workspaces/codeclimate-semgrep
collected 16 items

tests/test_cli.py ..........                                                                                                                                                                             [ 62%]
tests/cc/test_output.py ......                                                                                                                                                                           [100%]

============================================================================================== 16 passed in 3.15s ==============================================================================================
```

## ➤ Requirements

- **[Docker](https://gitlab.com/megabyte-labs/ansible-roles/docker)**
- [CodeClimate CLI](https://github.com/codeclimate/codeclimate)

### Optional Requirements

- [DockerSlim](https://gitlab.com/megabyte-labs/ansible-roles/dockerslim) - Used for generating compact, secure images
- [Google's Container structure test](https://github.com/GoogleContainerTools/container-structure-test) - For testing the Docker images


### Building the Docker Container

Run the below make command from the root of this repository to create a local fat docker image
```shell
make image
```

### Building a Slim Container

Run the below make command from the root of this repository to create a local slim docker image
```shell
make slim
```

### Test

Run the below command from the root of this repository to test the images created by this repository.
```shell
make test
```

## Authors

[Gabriel Gironda](mailto:gabriel@gironda.org)
