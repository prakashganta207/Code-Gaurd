"""Load settings from ``configs/default.yaml``, ``.env`` and environment variables.

Precedence, lowest to highest: YAML file < ``.env`` file < real environment variables.
The result is one typed, validated, immutable :class:`Settings` object.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field

#: Project root in the src layout: src/codeguard/config.py -> parents[2].
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "default.yaml"

#: Environment variable -> (section, key) in the YAML.
ENV_OVERRIDES: dict[str, tuple[str, str]] = {
    "OLLAMA_HOST": ("ollama", "host"),
    "MODEL_NAME": ("ollama", "model"),
    "MAX_REPAIR_ROUNDS": ("repair", "max_rounds"),
}


class _Section(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OllamaSettings(_Section):
    host: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    timeout_s: float = Field(gt=0)
    max_retries: int = Field(ge=0)


class RepairSettings(_Section):
    max_rounds: int = Field(ge=1)


class PathSettings(_Section):
    data_dir: Path
    runs_dir: Path
    class_map: Path


class Settings(_Section):
    seed: int
    ollama: OllamaSettings
    repair: RepairSettings
    paths: PathSettings


def load_settings(
    config_path: Path | None = None,
    env_file: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Build the effective settings.

    Args:
        config_path: YAML file. Defaults to ``$CODEGUARD_CONFIG`` or ``configs/default.yaml``.
        env_file: ``.env`` file. Defaults to ``<project root>/.env``; a missing file is fine.
        environ: Environment to read overrides from. Defaults to ``os.environ`` (tests pass
            a dict instead).

    Returns:
        Validated settings, with relative paths resolved against the project root.
    """
    environ = os.environ if environ is None else environ
    config_path = Path(config_path or environ.get("CODEGUARD_CONFIG") or DEFAULT_CONFIG)
    root = config_path.resolve().parent.parent
    env_file = env_file or root / ".env"

    raw: dict[str, Any] = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}

    file_env = {k: v for k, v in dotenv_values(env_file).items() if v is not None}
    for source in (file_env, environ):
        for var, (section, key) in ENV_OVERRIDES.items():
            if var in source:
                raw.setdefault(section, {})[key] = source[var]

    paths = raw.get("paths", {})
    for key, value in paths.items():
        p = Path(value)
        paths[key] = p if p.is_absolute() else root / p

    return Settings.model_validate(raw)
