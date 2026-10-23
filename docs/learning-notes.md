# Learning notes

Plain-English explanations of every concept we use, added phase by phase.

---

## Phase 0: Setup

### Virtual environments and why the Python version is pinned
A virtualenv (`.venv`) is a private copy of Python plus its own installed packages, separate from
the system. Two reasons it matters more in ML than in typical web work:
1. **Binary wheels.** PyTorch ships huge pre-compiled packages built per Python version *and* per
   CUDA version. A brand-new Python (we have 3.14 on the machine) often has no matching GPU wheels
   yet, or has subtly different ones. Pinning 3.11 keeps us on the most battle-tested combination.
2. **Reproducibility.** A metric is only meaningful if someone else can re-run it and get the same
   number. Same Python + same package versions + same random seed → same result.

### GPU driver vs CUDA toolkit
- The **driver** (`nvidia-smi` shows ours: 610.88) lets programs talk to the GPU. It reports the
  *newest* CUDA version it can run (13.x), not one that's installed.
- The **CUDA toolkit** (`nvcc`) is a compiler for writing your own GPU code. We don't need it:
  PyTorch wheels bundle the CUDA runtime libraries they were built against. We just need a driver
  new enough to run them, and ours is.

### The 8 GB VRAM budget
VRAM is the GPU's own memory. Everything the GPU computes on must fit there at once:
- **Ollama, Qwen 7B at 4-bit**: 7 billion weights × ~0.5 bytes ≈ 4–5 GB, plus working memory.
- **CodeBERT training**: 125M weights is small, but training also stores gradients, optimizer
  state (Adam keeps 2 extra numbers per weight) and *activations*: intermediate results for every
  token in the batch, which grow with batch size × sequence length (512).

Both together would not fit in 8 GB, which is why they must never run simultaneously. Tricks we'll
use for training:
- **fp16 / mixed precision**: store most numbers in 16 bits instead of 32 → roughly half the memory,
  and faster on RTX tensor cores. A "loss scaler" prevents tiny gradients from rounding to zero.
- **Small batch + gradient accumulation**: run e.g. 4 batches of 8, add up their gradients, then
  update once. The model "sees" an effective batch of 32 while memory only holds 8 at a time.

### Pre-commit, ruff, black, CI
- **black** formats code so style is never a discussion.
- **ruff** is a fast linter: catches unused imports, bugs (bugbear rules) and even some insecure
  patterns (its `S` rules are a Bandit port, fitting for this project).
- **pre-commit** runs both automatically on every `git commit`, so bad code never enters history.
- **CI (GitHub Actions)** repeats the same checks plus `pytest` on a clean Linux machine for every
  push. This catches "works on my machine" problems. Tests that need a GPU or Ollama are marked and
  skipped there, because CI runners have neither.

### Typed contracts between modules (`schemas.py`)
Code Guard has several parts (detectors, fusion, repair, reporting, evaluation) that hand data to
each other. `schemas.py` defines the *only* shapes allowed to cross those boundaries: `Finding`,
`Detection`, `RepairAttempt` and `Report`. Think of them like an API contract between microservices,
except inside one program.

They are **pydantic** models, which means the data is checked when an object is created:
- `confidence=1.5` or `line=0` raises an error immediately, instead of producing a weird number
  three steps later.
- `extra="forbid"` rejects unknown fields, so a typo like `vuln_clas=` fails loudly.
- `frozen=True` makes objects immutable, so the repair loop can't accidentally change a detection
  that the report later relies on.
- Validators enforce rules *between* fields, such as "a vulnerable `Detection` must have at least one
  finding and a `top_class` that isn't `safe`."

Why this matters for ML work: most bugs in data pipelines are not crashes. They are silently wrong
values, like a mislabelled sample or a confidence on the wrong scale, and those quietly corrupt
your metrics. Validating at the boundaries is cheap insurance.

### Layered configuration (`config.py`)
Settings come from three layers, each overriding the one before:
1. `configs/default.yaml`: committed defaults, the same for everyone.
2. `.env`: per-machine values (not committed), e.g. a different Ollama host.
3. Real environment variables: per-run overrides, e.g. `MODEL_NAME=... make baseline`.

All three merge into one validated `Settings` object. Code never reads `os.environ` or hard-codes a
model name or path; it asks `load_settings()`. This is the
[12-factor](https://12factor.net/config) idea you may know from DevOps. For experiments it has an
extra benefit: the exact settings of a run can be printed (`codeguard config`) and saved next to
its results, so every number is traceable to its configuration.

### Architecture tests
`tests/unit/test_architecture.py` reads every source file's `import` statements (using Python's
`ast` module, which turns code into a tree you can inspect) and fails if a module rule is broken,
for example if `codeguard` ever imports `eval`. Rules written only in documentation get broken
eventually; rules enforced by CI tend to stay intact.
