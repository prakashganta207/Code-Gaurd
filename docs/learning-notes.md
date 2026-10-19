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
