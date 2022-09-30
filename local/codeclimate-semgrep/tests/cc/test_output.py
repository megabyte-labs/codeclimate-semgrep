from pathlib import Path

import codeclimate_semgrep.semgrep.output as semgrep
import pytest
from codeclimate_semgrep import cc


@pytest.fixture
def result():
    return semgrep.Result(
        check_id="foo",
        start=semgrep.Location(col=1, line=1),
        end=semgrep.Location(col=32, line=1),
        path="/example/foo.py",
        extra=semgrep.Extra(
            message="foo",
            severity=semgrep.Severity.WARNING,
            metadata=semgrep.Metadata(),
        ),
    )


def test_categories_default_to_bug_risk(result):
    assert cc.output_from_semgrep_result(result, Path("/example")).categories == [
        cc.output.Category.BUG_RISK
    ]


def test_categories_set_from_metadata(result):
    result.extra.metadata.cc_categories = [
        semgrep.CcCategory.BUG_RISK,
        semgrep.CcCategory.CLARITY,
    ]

    assert cc.output_from_semgrep_result(result, Path("/example")).categories == [
        cc.output.Category.BUG_RISK,
        cc.output.Category.CLARITY,
    ]


def test_severity_mapped_from_semgrep_severity(result):
    sem_to_cc_sev = {
        semgrep.Severity.WARNING: cc.output.Severity.MINOR,
        semgrep.Severity.ERROR: cc.output.Severity.MAJOR,
        semgrep.Severity.INFO: cc.output.Severity.INFO,
    }

    for (semsev, ccsev) in sem_to_cc_sev.items():
        result.extra.severity = semsev
        assert ccsev == cc.output_from_semgrep_result(result, Path("/example")).severity


def test_cc_severity_set_from_metadata(result):
    result.extra.severity = semgrep.Severity.ERROR
    result.extra.metadata.cc_severity = semgrep.CcSeverity.BLOCKER

    assert (
        cc.output.Severity.BLOCKER
        == cc.output_from_semgrep_result(result, Path("/example")).severity
    )


def test_dash_check_id_maps_to_inline_check_name(result):
    result.check_id = "-"

    assert (
        cc.output_from_semgrep_result(result, Path("/example")).check_name
        == "Semgrep/InlinePattern"
    )


def test_check_id_maps_to_check_name_prefixed_with_semgrep(result):
    assert (
        cc.output_from_semgrep_result(result, Path("/example")).check_name
        == f"Semgrep/{result.check_id}"
    )
