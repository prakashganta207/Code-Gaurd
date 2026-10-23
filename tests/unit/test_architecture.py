"""Enforce the module rules from CLAUDE.md by reading import statements."""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "codeguard"
DETECTOR_FAMILIES = ("codeguard.detectors.static", "codeguard.detectors.ml")


def imports_of(path: Path) -> set[str]:
    """Absolute module names imported by a file."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


ALL_FILES = sorted(SRC.rglob("*.py"))


@pytest.mark.parametrize("path", ALL_FILES, ids=lambda p: str(p.relative_to(SRC)))
def test_codeguard_never_imports_eval(path: Path) -> None:
    assert not any(m == "eval" or m.startswith("eval.") for m in imports_of(path))


@pytest.mark.parametrize("family", DETECTOR_FAMILIES)
def test_detector_families_do_not_import_each_other(family: str) -> None:
    folder = SRC / Path(*family.split(".")[1:])
    others = [f for f in DETECTOR_FAMILIES if f != family]
    for path in folder.rglob("*.py"):
        bad = [m for m in imports_of(path) for o in others if m.startswith(o)]
        assert not bad, f"{path.name} imports {bad}"


def test_cli_only_talks_to_pipeline_config_and_schemas() -> None:
    allowed = {"codeguard", "codeguard.pipeline", "codeguard.config", "codeguard.schemas"}
    own = {m for m in imports_of(SRC / "cli.py") if m.startswith("codeguard")}
    assert own <= allowed, own - allowed
