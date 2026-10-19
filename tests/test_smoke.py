"""Smoke test: the package imports and the class list matches the project spec."""

import codeguard


def test_classes_are_fixed() -> None:
    assert codeguard.CLASSES == (
        "sql_injection",
        "xss",
        "command_injection",
        "path_traversal",
        "code_execution",
        "safe",
    )
