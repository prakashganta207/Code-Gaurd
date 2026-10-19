# Code Guard

Detect and automatically repair security vulnerabilities in LLM-generated Python code.

A local LLM generates code → static analysis (Bandit + Semgrep) and a fine-tuned CodeBERT classifier
scan it → a fusion step decides → a repair agent asks the LLM to fix it (max 3 rounds) → CodeQL
independently judges the final result.

> 🚧 Work in progress. See [CLAUDE.md](CLAUDE.md) for status and
> [docs/architecture.md](docs/architecture.md) for the design.

## Dev setup (Windows)

```powershell
py install 3.11                      # Python Install Manager
py -V:3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e . -r requirements-dev.txt
pre-commit install
python scripts/check_env.py
pytest
```

ML extras (from Phase 3 on): install the CUDA build of PyTorch using the command from
<https://pytorch.org/get-started/locally/>, then `pip install -r requirements-ml.txt`.
