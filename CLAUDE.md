# CLAUDE.md: Code Guard project memory

Portfolio project by a 3rd-year CSE student (DevOps/fullstack background, new to ML). **Teach, don't
just deliver**: plain-English explanations go in `docs/learning-notes.md`.

## Working agreement
- One phase at a time. Before coding a phase: a 5–10 line plan + the key concept. After: run it, show
  results, update this file + learning-notes, commit, then **stop and wait for go-ahead**.
- If a fixed decision turns out wrong (dataset moved, tool misbehaves, VRAM doesn't fit): stop and
  present options. Never silently work around it.
- **Never fabricate** results, dataset sizes or metrics. Every number comes from running code.
- Readable over clever. Type hints + docstrings on public functions.
- Tests required for: static-finding normalizer, fusion logic, repair loop.

## Fixed decisions (change only with user approval)
- Python code only. Classes (canonical order, see `codeguard.CLASSES`): `sql_injection`, `xss`,
  `command_injection`, `path_traversal`, `code_execution`, `safe`.
- Generator: Qwen2.5-Coder 7B Instruct via Ollama, 4-bit. *Before Phase 1: check for a newer
  comparable coder model in the 7B class and let the user choose.*
- Detector: `microsoft/codebert-base`, sequence classification, max_len 512, fp16, small batch +
  grad accumulation. Training data: VUDENC (Wartschinski et al., arXiv 2201.08441), function-level.
- Split VUDENC **by repository**. Handle imbalance. Report per-class P/R/F1 + macro-F1. Clean noisy
  labels and log drops. Fixed seeds. All experiments in MLflow.
- Benchmarks: SecurityEval (121 Python prompts) + CyberSecEval instruct, Python subset (PurpleLlama).
  Official sources only.
- **Judge = CodeQL only.** Bandit/Semgrep guide repairs and must never be the judge.
- Repair: prompting loop, max 3 rounds. LoRA repair model = stretch goal.
- A "fix" that breaks parsing / tests / deletes functionality = failure.
- Stack: Python 3.11, PyTorch, HF transformers/datasets, MLflow, FastAPI, React (Vite), Docker
  Compose, GitHub Actions, pytest.

## Machine facts (checked 2026-10-20)
- Windows 11 Home. Repo path `E:\Code Gaurd` (has a space; quote paths).
- RTX 4060 Laptop, 8 GB VRAM, driver 610.88 (CUDA 13.x capable). No CUDA toolkit needed.
- **Ollama and training must never run at the same time** (8 GB VRAM). `ollama stop <model>` first.
- Ollama 0.40.5 installed; only `qwen2.5:latest` (general, NOT coder) pulled.
- Node 25.8 / npm 11.11, git 2.56.

## Conventions
- src layout: package at `src/codeguard`, install with `pip install -e .`.
- Deps: `requirements.txt` (core), `requirements-ml.txt` (ML; torch installed separately from the
  PyTorch CUDA index), `requirements-dev.txt` (lint/test, pins match pre-commit).
- Lint: ruff + black, line length 100. Pytest markers `gpu`, `ollama` are skipped in CI.
- `data/`, `models/`, `mlruns/` are gitignored. Never commit datasets or weights.
- Seeds: use 42 unless an experiment says otherwise.
- Env check: `.venv\Scripts\python scripts/check_env.py` (finds venv tools without activation).
- Python 3.11 was installed via `py install 3.11` (Python Install Manager); default `py` is 3.14.

## Progress
- [x] Phase 0, Setup: skeleton, pyproject, requirements, pre-commit, CI. Python 3.11.9 venv at
  `.venv`; pre-commit hooks installed and passing; pytest passing.
- [ ] Phase 1, Baseline
- [ ] Phase 2, Static repair loop (MVP)
- [ ] Phase 3, Dataset
- [ ] Phase 4, Train classifier
- [ ] Phase 5, Fusion
- [ ] Phase 6, Full evaluation
- [ ] Phase 7, Product
- [ ] Phase 8, Polish

## Open issues
- Semgrep 1.181.0 works natively on Windows (verified with a local rule). BUT `p/python` (151
  rules) gave 0 findings on `os.system(input())`, so registry rules seem framework-taint-focused.
  Phase 1 must pick rulesets deliberately and likely add custom rules for our 5 classes.
- Docker, CodeQL CLI not installed yet (user installs manually).
- Global Python 3.14 has an unrelated CPU-only torch; irrelevant to `.venv`.
