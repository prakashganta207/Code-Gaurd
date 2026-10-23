"""Shared data types passed between detectors, fusion, repair and reporting.

These are the *only* shapes that cross module boundaries. Every model is immutable
(``frozen``) and rejects unknown fields, so a typo or a half-built object fails loudly at
the boundary instead of silently propagating.
"""

from __future__ import annotations

from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator

from codeguard import CLASSES, VULN_CLASSES

VulnClass = Literal["sql_injection", "xss", "command_injection", "path_traversal", "code_execution"]
#: A finding is always *something* flagged: one of our classes, or ``other`` for an
#: unmapped rule. It is never ``safe``.
FindingClass = Literal[VulnClass, "other"]
#: The overall verdict for a piece of code.
DetectionClass = Literal[FindingClass, "safe"]
Severity = Literal["low", "medium", "high"]
Source = Literal["bandit", "semgrep", "ml"]
ReportStatus = Literal["clean", "fixed", "unresolved"]

# Guard against the Literal drifting away from the canonical class list.
assert get_args(VulnClass) == VULN_CLASSES  # noqa: S101
assert (*VULN_CLASSES, "safe") == CLASSES  # noqa: S101


class _Model(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Finding(_Model):
    """One issue reported by one detector."""

    vuln_class: FindingClass
    line: int | None = Field(
        default=None, ge=1, description="1-based line; None for function-level ML findings"
    )
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    source: Source
    rule_id: str
    message: str


class Detection(_Model):
    """The fused verdict for one piece of code."""

    is_vulnerable: bool
    findings: tuple[Finding, ...] = ()
    top_class: DetectionClass
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _verdict_is_consistent(self) -> Detection:
        if self.is_vulnerable and self.top_class == "safe":
            raise ValueError("a vulnerable detection cannot have top_class 'safe'")
        if not self.is_vulnerable and self.top_class != "safe":
            raise ValueError("a non-vulnerable detection must have top_class 'safe'")
        if self.is_vulnerable and not self.findings:
            raise ValueError("a vulnerable detection needs at least one finding")
        return self

    @classmethod
    def clean(cls, confidence: float = 1.0) -> Detection:
        """A 'nothing found' verdict."""
        return cls(is_vulnerable=False, top_class="safe", confidence=confidence)


class RepairAttempt(_Model):
    """One round of the repair loop."""

    round: int = Field(ge=1)
    code_before: str
    code_after: str
    detection_before: Detection
    detection_after: Detection | None = Field(
        default=None, description="None when the LLM output did not parse as Python"
    )
    parses: bool = True

    @model_validator(mode="after")
    def _unparsed_has_no_detection(self) -> RepairAttempt:
        if not self.parses and self.detection_after is not None:
            raise ValueError("an unparseable repair cannot have a detection_after")
        if self.parses and self.detection_after is None:
            raise ValueError("a parseable repair must have a detection_after")
        return self


class Report(_Model):
    """End result of one pipeline run."""

    prompt: str | None = Field(default=None, description="None when scanning an existing file")
    initial_detection: Detection
    final_code: str
    attempts: tuple[RepairAttempt, ...] = ()
    status: ReportStatus
