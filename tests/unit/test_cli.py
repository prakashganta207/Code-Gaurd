"""Tests for the CLI surface (not behaviour; that lives in the pipeline)."""

import pytest

from codeguard.cli import main


def test_help_exits_cleanly(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for command in ("scan", "generate", "repair", "config"):
        assert command in out


def test_config_prints_settings(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["config"]) == 0
    assert '"max_rounds"' in capsys.readouterr().out
