# Code Guard

Detect and automatically repair security vulnerabilities in LLM-generated Python code.

A local LLM generates code → static analysis (Bandit + Semgrep) and, later, a fine-tuned CodeBERT
classifier scan it → a fusion step decides → a repair agent asks the LLM to fix it (max 3 rounds) →
CodeQL independently judges the final result.

> 🚧 Work in progress. See [CLAUDE.md](CLAUDE.md) for status and
> [docs/architecture.md](docs/architecture.md) for the design.

## Dev setup

Requires Python 3.11 and GNU make (Windows: `py install 3.11`, `winget install ezwinports.make`).

```bash
make setup        # venv + editable install + pre-commit hooks
make lint
make test
make check-env    # what's installed, is Ollama running
codeguard --help  # from the activated venv
```

Settings live in `configs/default.yaml`; copy `.env.example` to `.env` for per-machine overrides.
