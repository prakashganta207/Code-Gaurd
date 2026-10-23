# CLAUDE.md: Code Guard project memory

Solo portfolio project by a 3rd-year CSE student (DevOps/fullstack background, new to ML).
**Teach, don't just deliver**: plain-English explanations go in `docs/learning-notes.md`.
Current scope: **Phases 0–3 only**. Do not start Phase 4 (training) or later.

## Working agreement
- Before each phase: 5–10 line plan + the key concept, then **wait for OK**.
- During: tests alongside code; explain new concepts in learning-notes.
- End of phase: run everything, show results + acceptance checklist, update Progress below,
  merge to `main`, tag, push, then **STOP and wait**.
- Branch per phase: `phase-0/setup`, `phase-1/baseline`, `phase-2/mvp`, `phase-3/dataset`.
  Commit prefixes: `feat:`, `fix:`, `data:`, `test:`, `docs:`, `chore:`.
- If something in the spec is wrong (dataset moved, tool misbehaves, doesn't fit 8 GB): stop and
  give options. Never work around it silently.
- **Never fabricate** numbers, dataset sizes or results. Every number comes from code that ran.
- Save LLM generations to `runs/` and reuse them; never regenerate unless the user asks.
- Readable over clever. Type hints + docstrings on public functions.

## Fixed decisions (change only with user approval)
- Python code only. Classes (canonical order in `codeguard.CLASSES`): `sql_injection`, `xss`,
  `command_injection`, `path_traversal`, `code_execution`, `safe`. Findings may also be `other`
  (unmapped rule; logged, never dropped). A Finding is never `safe`.
- Generator: Qwen2.5-Coder 7B Instruct via Ollama, 4-bit, temperature 0. *Start of Phase 1: check
  for a newer comparable coder model in the 7B class and let the user choose.*
- Static detectors: Bandit + Semgrep. **Judge = CodeQL only**; Bandit/Semgrep never judge.
- Benchmark (Phases 1–2): SecurityEval, 121 Python prompts, official source only.
- Training data (Phase 3): VUDENC, official source from arXiv 2201.08441. Function-level, split
  80/10/10 **by project**, cleaning with logged drop reasons, no silent truncation at 512 tokens.
- Repair loop: max `MAX_REPAIR_ROUNDS` (default 3); unparseable LLM output = failed round.
- Stack: Python 3.11, pytest, ruff, black, pre-commit, GitHub Actions; MLflow later.

## Module rules (enforced by tests/unit/test_architecture.py where possible)
1. Only `pipeline.py` knows the order of steps.
2. Detectors never import each other; fusion is the only place they meet.
3. `eval/` may import `codeguard`; `codeguard` must never import `eval/`.
4. The CLI holds no logic: parse input, call the pipeline, print output.
5. No hard-coded paths or model names: everything from `configs/` and `.env` via `config.py`.

## Structure
- `configs/default.yaml` pipeline settings; `configs/class_map.yaml` rule ID → class (Phase 2).
- `src/codeguard/`: `schemas.py` (Finding, Detection, RepairAttempt, Report: frozen pydantic,
  extra=forbid), `config.py` (`load_settings()`), `cli.py`, `detectors/base.py` (Detector
  protocol), plus packages `generator/`, `detectors/{static,ml}/`, `fusion/`, `repair/`, `report/`.
- `eval/` (`benchmarks/`, `judge/`, metrics, run_eval). Run as `python -m eval.run_eval`.
- `tests/{unit,integration,fixtures}`. `data/{raw,interim,processed}` and `runs/` are gitignored.
- `api/`, `web/`: README placeholders only.

## Conventions
- Install: `make setup` (venv + `pip install -e ".[dev]"` + pre-commit). ML extras: `.[ml]`, with
  the CUDA PyTorch wheel installed separately first.
- `make lint` (ruff + black, line length 100), `make test` (pytest `-m "not slow"`).
  Mark tests needing GPU/Ollama/CodeQL/network with `@pytest.mark.slow`; CI excludes them.
- Config precedence: YAML < `.env` < environment. Env vars: `OLLAMA_HOST`, `MODEL_NAME`,
  `MAX_REPAIR_ROUNDS`, `CODEGUARD_CONFIG` (alternate YAML). Relative paths resolve to project root.
- Seed 42. `make check-env` reports the toolchain and whether the Ollama server is up.
- `codeguard config` prints effective settings.

## Machine facts (checked 2026-10-23)
- Windows 11 Home. Repo path `E:\Code Gaurd` (has a space; quote paths). Remote:
  github.com/prakashganta207/Code-Gaurd. `gh` CLI is not authenticated (can't read CI status).
- RTX 4060 Laptop, 8 GB VRAM, driver 610.88. **Ollama and training never run at the same time.**
- Python 3.11.9 via `py install 3.11` (default `py` is 3.14). GNU Make 4.4.1 via winget
  (`ezwinports.make`); recipes run under cmd.exe on Windows, so the Makefile uses backslash paths.
- Ollama 0.40.5; only `qwen2.5:latest` (general, NOT coder) pulled; server not auto-running.
- Bandit 1.9.4, Semgrep 1.181.0 work natively. **Missing: CodeQL CLI (blocks Phase 1), Docker.**

## Progress
- [x] Phase 0, Setup: restructured to the Phases 0–3 spec; schemas, config, CLI stubs, Makefile,
  CI via make; 37 unit tests pass. Tag `v0.0-setup`.
- [ ] Phase 1, Baseline (`v0.1-baseline`)
- [ ] Phase 2, Static repair loop / MVP (`v0.2-mvp`)
- [ ] Phase 3, Dataset (`v0.3-dataset`)

## Open issues
- Semgrep `p/python` (151 rules) gave 0 findings on `os.system(input())`: registry rules look
  framework-taint-focused. Phase 1 must choose rulesets deliberately (likely + custom rules).
- Global Python 3.14 has an unrelated CPU-only torch; irrelevant to `.venv`.
