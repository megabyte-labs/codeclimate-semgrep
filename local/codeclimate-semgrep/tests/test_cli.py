# type: ignore
import inspect
import json
import pathlib
from itertools import zip_longest
from textwrap import dedent

import pytest
from codeclimate_semgrep.cli import Cli


# Used as a test value for semgrep patterns to match on
def _sentinel():
    raise RuntimeError("Testing")


_SENTINEL_START_COL = 1
_lines, _SENTINEL_START_LINE = inspect.getsourcelines(_sentinel)
_SENTINEL_END_LINE = _SENTINEL_START_LINE + len(_lines) - 1
_SENTINEL_END_COL = len(_lines[-1])

# Patterns to match the above sentinel definition and the expected matches
sentinel_def_pattern = {"pattern": "def _sentinel(...):...", "lang": "py"}
sentinel_body_pattern = {"pattern": "raise RuntimeError('Testing')", "lang": "py"}


@pytest.fixture
def test_file_def_match(test_file):
    return {
        "type": "issue",
        "check_name": "Semgrep/InlinePattern",
        "description": "def _sentinel(...):...",
        "categories": ["Bug Risk"],
        "severity": "major",
        "location": {
            "path": str(test_file),
            "positions": {
                "begin": {
                    "line": _SENTINEL_START_LINE,
                    "column": _SENTINEL_START_COL,
                },
                "end": {"line": _SENTINEL_END_LINE, "column": _SENTINEL_END_COL},
            },
        },
    }


@pytest.fixture
def test_file_body_match(test_file):
    return {
        "type": "issue",
        "check_name": "Semgrep/InlinePattern",
        "description": "raise RuntimeError('Testing')",
        "categories": ["Bug Risk"],
        "severity": "major",
        "location": {
            "path": str(test_file),
            "positions": {
                "begin": {"line": _SENTINEL_START_LINE + 1, "column": 5},
                "end": {"line": _SENTINEL_START_LINE + 1, "column": 34},
            },
        },
    }


@pytest.fixture
def test_file(test_dir):
    return pathlib.Path(__file__).relative_to(test_dir)


@pytest.fixture
def test_dir():
    return pathlib.Path(__file__).parent


@pytest.fixture
def config(tmp_path: pathlib.Path, test_file):
    def _config(**kwargs):
        config_file = tmp_path / "config.json"
        config = {
            "runs": [],
            "include_paths": [str(test_file)],
            **kwargs,
        }

        with config_file.open("w") as f:
            json.dump(config, f)

        return str(config_file)

    return _config


@pytest.fixture
def cli(tmp_path: pathlib.Path, test_dir: pathlib.Path):
    out_file = tmp_path / "output.json"
    err_file = tmp_path / "err.out"

    def _cli(
        config: str,
        dir: str = str(test_dir),
        out: str = str(out_file),
        err: str = str(err_file),
    ):

        argv = [
            "--config",
            str(config),
            "--dir",
            dir,
            "--out",
            out,
            "--err",
            err,
        ]

        return (Cli(argv=argv), out_file, err_file)

    return _cli


def test_cli_run_with_empty_output(cli, config):
    c, out, err = cli(config(runs=[{"pattern": "willnotmatch(...)", "lang": "go"}]))
    c.run()

    assert out.read_text() == ""
    assert err.read_text() == ""


def test_cli_run_with_results(cli, config, test_file_def_match, test_file_body_match):
    c, out, err = cli(config(runs=[sentinel_def_pattern, sentinel_body_pattern]))

    c.run()
    assert err.read_text() == ""

    expecteds = [test_file_def_match, test_file_body_match]
    actuals = map(json.loads, out.read_text().split("\0"))

    for (expected, actual) in zip_longest(expecteds, actuals):
        assert expected == actual


def test_cli_run_with_results_and_errors(
    cli, config, test_file_def_match, test_file_body_match
):
    runs = [
        sentinel_def_pattern,
        {"pattern": "|BADPATTERN|", "lang": "py"},
        {"pattern": "|ANOTHER-BADPATTERN|", "lang": "py"},
        sentinel_body_pattern,
    ]
    c, out, err = cli(config(runs=runs))

    c.run()

    expecteds = [test_file_def_match, test_file_body_match]
    actuals = map(json.loads, out.read_text().split("\0"))

    for (expected, actual) in zip_longest(expecteds, actuals):
        assert expected == actual

    expected_error = dedent(
        """
        semgrep error: invalid pattern
          --> CLI Input:1
        1 | |BADPATTERN|
          | ^^^^^^^^^^^

        Pattern could not be parsed as a Python semgrep pattern
        ----
        semgrep error: invalid pattern
          --> CLI Input:1
        1 | |ANOTHER-BADPATTERN|
          | ^^^^^^^^^^^^^^^^^^^

        Pattern could not be parsed as a Python semgrep pattern
        """
    ).lstrip()

    assert err.read_text() == expected_error


def test_cli_run_with_multiple_rules_files_in_single_run(
    cli, config, test_dir, test_file_def_match, test_file_body_match
):
    runs = [
        {
            "configs": [
                str(test_dir / "sentinel-definition.yml"),
                str(test_dir / "sentinel-body.yml"),
            ]
        }
    ]
    c, out, err = cli(config(runs=runs))

    c.run()

    expecteds = [
        {
            **test_file_def_match,
            "check_name": "Semgrep/tests.sentinel-definition",
            "description": "test sentinel function definition",
        },
        {
            **test_file_body_match,
            "check_name": "Semgrep/tests.sentinel-body",
            "description": "test sentinel body",
        },
    ]
    actuals = map(json.loads, out.read_text().split("\0"))

    for (expected, actual) in zip_longest(expecteds, actuals):
        assert expected == actual

    assert err.read_text() == ""


def test_cli_run_with_multiple_rules_files_across_runs(
    cli, config, test_dir, test_file_def_match, test_file_body_match
):
    runs = [
        {"configs": [str(test_dir / "sentinel-definition.yml")]},
        {"configs": [str(test_dir / "sentinel-body.yml")]},
    ]
    c, out, err = cli(config(runs=runs))

    c.run()

    expecteds = [
        {
            **test_file_def_match,
            "check_name": "Semgrep/tests.sentinel-definition",
            "description": "test sentinel function definition",
        },
        {
            **test_file_body_match,
            "check_name": "Semgrep/tests.sentinel-body",
            "description": "test sentinel body",
        },
    ]
    actuals = map(json.loads, out.read_text().split("\0"))

    for (expected, actual) in zip_longest(expecteds, actuals):
        assert expected == actual

    assert err.read_text() == ""


def test_cli_run_with_non_existent_rules_file_in_single_run(cli, config, test_dir):
    runs = [
        {"configs": [str(test_dir / "!nope.yml"), str(test_dir / "sentinel-body.yml")]}
    ]
    c, out, err = cli(config(runs=runs))

    c.run()

    assert out.read_text() == ""

    assert (
        err.read_text()
        == "unable to find a config; path `/workspaces/codeclimate-semgrep/tests/!nope.yml` does not exist"
    )


def test_cli_run_with_non_existent_rules_file_across_runs(
    cli, config, test_dir, test_file_body_match
):
    runs = [
        {"configs": [str(test_dir / "!nope.yml")]},
        {"configs": [str(test_dir / "sentinel-body.yml")]},
    ]
    c, out, err = cli(config(runs=runs))

    c.run()

    expecteds = [
        {
            **test_file_body_match,
            "check_name": "Semgrep/tests.sentinel-body",
            "description": "test sentinel body",
        },
    ]
    actuals = map(json.loads, out.read_text().split("\0"))

    for (expected, actual) in zip_longest(expecteds, actuals):
        assert expected == actual

    assert (
        err.read_text() == "no valid configuration file found (1 configs were invalid)"
    )


def test_cli_run_with_present_and_missing_files_runs_on_present_files(
    cli, config, test_dir, test_file, test_file_body_match
):
    runs = [{"configs": [str(test_dir / "sentinel-body.yml")]}]
    c, out, err = cli(config(runs=runs, include_paths=["nah", str(test_file)]))

    c.run()

    expecteds = [
        {
            **test_file_body_match,
            "check_name": "Semgrep/tests.sentinel-body",
            "description": "test sentinel body",
        },
    ]
    actuals = map(json.loads, out.read_text().split("\0"))

    for (expected, actual) in zip_longest(expecteds, actuals):
        assert expected == actual

    assert err.read_text() == ""


def test_cli_with_bad_out_path(cli, config, tmp_path, capsys):
    with pytest.raises(SystemExit):
        cli(config(), out=str(tmp_path / "non" / "existent"))

    captured = capsys.readouterr()
    assert "argument -o/--out: can't open" in captured.err


def test_cli_with_bad_err_path(cli, config, tmp_path, capsys):
    with pytest.raises(SystemExit):
        cli(config(), err=str(tmp_path / "non" / "existent"))

    captured = capsys.readouterr()
    assert "argument -e/--err: can't open" in captured.err
