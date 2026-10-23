"""Tests for settings loading and override precedence."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from codeguard.config import DEFAULT_CONFIG, load_settings

YAML = """\
seed: 42
ollama:
  host: http://yaml-host:11434
  model: yaml-model
  temperature: 0.0
  timeout_s: 60
  max_retries: 2
repair:
  max_rounds: 3
paths:
  data_dir: data
  runs_dir: runs
  class_map: configs/class_map.yaml
"""


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A throwaway project root with configs/default.yaml."""
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs" / "default.yaml").write_text(YAML, encoding="utf-8")
    return tmp_path


def load(project: Path, environ: dict[str, str] | None = None):
    return load_settings(project / "configs" / "default.yaml", environ=environ or {})


def test_repo_default_config_is_valid() -> None:
    s = load_settings(DEFAULT_CONFIG, env_file=Path("does-not-exist.env"), environ={})
    assert s.repair.max_rounds == 3
    assert s.ollama.temperature == 0.0
    assert s.seed == 42


def test_yaml_values_and_resolved_paths(project: Path) -> None:
    s = load(project)
    assert s.ollama.model == "yaml-model"
    assert s.paths.data_dir == project.resolve() / "data"
    assert s.paths.class_map == project.resolve() / "configs" / "class_map.yaml"


def test_env_file_overrides_yaml(project: Path) -> None:
    (project / ".env").write_text("MODEL_NAME=dotenv-model\nMAX_REPAIR_ROUNDS=2\n")
    s = load(project)
    assert s.ollama.model == "dotenv-model"
    assert s.repair.max_rounds == 2  # string from .env coerced to int


def test_environment_overrides_env_file(project: Path) -> None:
    (project / ".env").write_text("MODEL_NAME=dotenv-model\n")
    s = load(project, {"MODEL_NAME": "env-model", "OLLAMA_HOST": "http://env:1"})
    assert s.ollama.model == "env-model"
    assert s.ollama.host == "http://env:1"


def test_invalid_override_is_rejected(project: Path) -> None:
    with pytest.raises(ValidationError):
        load(project, {"MAX_REPAIR_ROUNDS": "0"})


def test_unknown_yaml_key_is_rejected(project: Path) -> None:
    cfg = project / "configs" / "default.yaml"
    cfg.write_text(YAML + "typo_key: 1\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load(project)
