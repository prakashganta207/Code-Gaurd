"""Report which parts of the Code Guard toolchain are available on this machine.

Run from the repo root inside the venv:  python scripts/check_env.py
Exits 0 always; it is a report, not a gate.
"""

from __future__ import annotations

import os
import shutil
import subprocess  # noqa: S404 - fixed, trusted commands only
import sys
import sysconfig

# Also search this interpreter's Scripts/bin dir, so venv tools are found without activation.
_SEARCH_PATH = os.pathsep.join([sysconfig.get_path("scripts"), os.environ.get("PATH", "")])


def _run(cmd: list[str]) -> str:
    """Run a command and return its first output line, or an error marker."""
    exe = shutil.which(cmd[0], path=_SEARCH_PATH)
    if exe is None:
        return "NOT FOUND"
    try:
        out = subprocess.run(  # noqa: S603
            [exe, *cmd[1:]], capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"ERROR ({exc})"
    text = (out.stdout or out.stderr).strip()
    return text.splitlines()[0] if text else f"exit code {out.returncode}"


def _torch_report() -> str:
    """Describe the installed PyTorch build and the GPU it sees."""
    try:
        import torch
    except ImportError:
        return "NOT INSTALLED (see requirements-ml.txt)"
    if not torch.cuda.is_available():
        return f"{torch.__version__}, CUDA NOT available (CPU-only build?)"
    props = torch.cuda.get_device_properties(0)
    return (
        f"{torch.__version__}, CUDA {torch.version.cuda}, {props.name}, "
        f"{props.total_memory / 1024**3:.1f} GB, fp16 ok, bf16={torch.cuda.is_bf16_supported()}"
    )


def main() -> None:
    """Print one line per tool."""
    py_ok = sys.version_info[:2] == (3, 11)
    rows = {
        "python": f"{sys.version.split()[0]} {'OK' if py_ok else '(expected 3.11!)'}",
        "torch": _torch_report(),
        "git": _run(["git", "--version"]),
        "docker": _run(["docker", "--version"]),
        "ollama": _run(["ollama", "--version"]),
        "bandit": _run(["bandit", "--version"]),
        "semgrep": _run(["semgrep", "--version"]),
        "codeql": _run(["codeql", "version"]),
        "node": _run(["node", "--version"]),
    }
    width = max(map(len, rows))
    for name, status in rows.items():
        print(f"{name:<{width}}  {status}")


if __name__ == "__main__":
    main()
