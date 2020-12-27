"""CLI entry point for codeclimate-semgrep"""
import argparse
import json
import pathlib
import sys
from typing import Callable, List, TextIO

from . import bridge
from .cc import config_from_dict, Config
from .util import delimited_writer


class Cli:  # pylint: disable=too-few-public-methods
    """CLI arg parsing and IO"""

    out: TextIO
    err: TextIO
    write_out: Callable[[str], None]
    write_err: Callable[[str], None]
    config: Config
    dir: pathlib.Path

    def __init__(self, argv: List[str]):
        parser = argparse.ArgumentParser(
            description="Run semgrep as a Code Climate engine"
        )

        parser.add_argument(
            "-c",
            "--config",
            type=argparse.FileType("r"),
            default="/config.json",
            help="path to the engine config",
        )
        parser.add_argument(
            "-d",
            "--dir",
            type=pathlib.Path,
            default="/code",
            help="path to the code directory",
        )
        parser.add_argument(
            "-o",
            "--out",
            type=argparse.FileType("w"),
            default="-",
            help="path to write output, defaults to stdout",
        )
        parser.add_argument(
            "-e",
            "--err",
            type=argparse.FileType("w"),
            default=sys.stderr,
            help="path to write errors, defaults to stderr",
        )
        args = parser.parse_args(argv)

        self.config = config_from_dict(json.load(args.config))
        self.dir = args.dir
        self.out = args.out
        self.err = args.err

        # Ignore here because `mypy` says:
        #
        #     Invalid self argument "Cli" to attribute function "write_out" with
        #     type "Callable[[str], None]"
        #
        # But it's not correct in doing so: https://github.com/python/mypy/issues/2427
        self.write_out = delimited_writer(args.out)  # type: ignore[assignment,misc]
        self.write_err = delimited_writer(args.err, "----\n")  # type: ignore[assignment,misc]

    def run(self) -> None:
        """Invoke semgrep and handle results"""
        results = bridge.run(
            pathlib.Path(self.dir),
            self.config,
            on_error=lambda exc: self.write_err(str(exc)),  # type: ignore[call-arg, misc]
        )

        for result in results:
            self.write_out(json.dumps(result.to_dict()))  # type: ignore[call-arg, misc]

        self.out.close()
        self.err.close()


def run():  # pylint: disable=missing-function-docstring
    Cli(sys.argv[1:]).run()
