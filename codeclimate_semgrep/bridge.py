"""Semgrep invocation and bridging to Code Climate output

This module contains the functionality for invoking Semgrep and retrieving the
results in the Code Climate analysis engine output format.
"""
import json
import pathlib
from io import StringIO
from typing import Callable, Generator, List, Optional, TypedDict, Union

from semgrep.constants import OutputFormat  # type: ignore
from semgrep.error import SemgrepError  # type: ignore
from semgrep.output import OutputSettings, managed_output  # type: ignore
from semgrep.semgrep_main import main as semgrep_main  # type: ignore

from .cc import output_from_semgrep_result
from .cc.config import Config
from .cc.output import Output

# Ignore due to what may be a mypy bug, since pyright type checks this just
# fine: https://github.com/python-poetry/poetry/issues/3094
from .semgrep.output import Result, output_from_dict  # type: ignore[import]


class InvokeFromConfigsArgs(TypedDict):
    """Arguments specifying a Semgrep run from one or more configuration files

    Attributes:
        configs: A list of paths to Semgrep configuration files.
    """

    configs: List[str]


class InvokeFromInlineArgs(TypedDict):
    """Arguments specifying a Semgrep run from an inline-defined configuration

    Attributes:
        pattern: A Semgrep pattern to search for.
        lang: The language the pattern applies to.
        exclude: A list of globs specifying files to exclude.
        include: A list of globs specifying files to include.
    """

    pattern: str
    lang: str
    exclude: Optional[List[str]]
    include: Optional[List[str]]


def _invoke(
    paths: List[str], **kwargs: Union[InvokeFromConfigsArgs, InvokeFromInlineArgs]
) -> List[Result]:
    """Wrap Semgrep invocation

    The Semgrep public API basically consists of one function, `invoke_semgrep`
    (https://git.io/JLXog). We want to customize the invocation a little more
    and allow for things such as inline pattern definitions, so this performs
    much the same task of wrapping Semgrep.

    Args:
        paths: The list of paths to invoke Semgrep against.
        **kwargs: The configuration options to use when invoking Semgrep.

    Returns:
        A list of the results of the Semgrep invocation. Any errors are handled
        as exceptions, not returned as results.

    Raises:
        semgrep.error.SemgrepError: Any exception that Semgrep classes as a
            Semgrep error. Your guess is as good as mine.
    """

    output_settings = OutputSettings(
        output_format=OutputFormat.JSON,
        output_destination=None,
        error_on_findings=False,
        verbose_errors=False,
        strict=False,
        json_stats=False,
        output_per_finding_max_lines_limit=None,
    )

    io_capture = StringIO()

    with managed_output(output_settings) as output_handler:
        output_handler.stdout = io_capture
        semgrep_main(output_handler=output_handler, target=paths, **kwargs)

    parsed = json.loads(io_capture.getvalue())

    return output_from_dict(parsed).results


def run(
    rundir: pathlib.Path, config: Config, on_error: Callable[[Exception], None]
) -> Generator[Output, None, None]:
    """Run Semgrep and yield results in Code Climate engine format

    Args:
        rundir: The path to the codebase to analyze.
        config: The configuration for this analysis.
        on_error: A callback that will be invoked with Semgrep exceptions.
    Yields:
        Output: A Code Climate analysis engine output for each result from the
            Semgrep invocation.
    """
    paths = [
        str(p) for p in (rundir / path for path in config.include_paths) if p.exists()
    ]

    for run_config in config.runs:
        try:
            for result in _invoke(paths=paths, **vars(run_config)):
                yield output_from_semgrep_result(result, rundir=rundir)
        except SemgrepError as exc:
            on_error(exc)
            continue
