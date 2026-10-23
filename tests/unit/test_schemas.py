"""Tests for the shared data types."""

import pytest
from pydantic import ValidationError

import codeguard
from codeguard.schemas import Detection, Finding, RepairAttempt, Report


def make_finding(**overrides: object) -> Finding:
    data = {
        "vuln_class": "sql_injection",
        "line": 3,
        "severity": "high",
        "confidence": 0.9,
        "source": "bandit",
        "rule_id": "B608",
        "message": "Possible SQL injection via string-based query construction.",
    }
    data.update(overrides)
    return Finding(**data)


def test_classes_are_fixed() -> None:
    assert codeguard.CLASSES == (
        "sql_injection",
        "xss",
        "command_injection",
        "path_traversal",
        "code_execution",
        "safe",
    )
    assert codeguard.VULN_CLASSES == codeguard.CLASSES[:-1]


def test_finding_accepts_other_but_not_safe() -> None:
    assert make_finding(vuln_class="other").vuln_class == "other"
    with pytest.raises(ValidationError):
        make_finding(vuln_class="safe")


@pytest.mark.parametrize(
    "field, value",
    [("line", 0), ("confidence", 1.5), ("severity", "critical"), ("source", "codeql")],
)
def test_finding_rejects_invalid_values(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        make_finding(**{field: value})


def test_finding_line_optional_for_ml() -> None:
    assert make_finding(source="ml", line=None).line is None


def test_finding_is_immutable_and_strict() -> None:
    f = make_finding()
    with pytest.raises(ValidationError):
        f.line = 5  # type: ignore[misc]
    with pytest.raises(ValidationError):
        make_finding(unexpected="field")


def test_detection_clean() -> None:
    d = Detection.clean()
    assert not d.is_vulnerable and d.top_class == "safe" and d.findings == ()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"is_vulnerable": True, "top_class": "safe", "findings": (make_finding(),)},
        {"is_vulnerable": False, "top_class": "sql_injection"},
        {"is_vulnerable": True, "top_class": "sql_injection", "findings": ()},
    ],
)
def test_detection_rejects_inconsistent_verdicts(kwargs: dict) -> None:
    with pytest.raises(ValidationError):
        Detection(confidence=0.5, **kwargs)


def test_repair_attempt_parse_consistency() -> None:
    before = Detection(
        is_vulnerable=True, findings=(make_finding(),), top_class="sql_injection", confidence=0.9
    )
    ok = RepairAttempt(
        round=1,
        code_before="a",
        code_after="b",
        detection_before=before,
        detection_after=Detection.clean(),
    )
    assert ok.parses
    broken = RepairAttempt(
        round=2, code_before="b", code_after="def (", detection_before=before, parses=False
    )
    assert broken.detection_after is None
    with pytest.raises(ValidationError):
        RepairAttempt(round=1, code_before="a", code_after="b", detection_before=before)


def test_report_round_trips_through_json() -> None:
    report = Report(
        prompt="write a login handler",
        initial_detection=Detection.clean(),
        final_code="print('hi')\n",
        status="clean",
    )
    assert Report.model_validate_json(report.model_dump_json()) == report
