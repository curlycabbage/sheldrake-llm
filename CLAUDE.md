# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project

Experimental framework testing whether human operator presence affects deterministic LLM inference outputs. See docs/HYPOTHESIS.md for the full pre-registration and docs/PROTOCOL.md for the experimental procedure.

## Key Files

- `config/default.yaml` — all configurable parameters (model path, seed, prompts, run counts)
- `scripts/baseline.py` — Phase 2: baseline noise floor characterization
- `scripts/experiment.py` — Phase 3: operator condition runs
- `scripts/analyze.py` — Phase 4: analysis and visualization
- `scripts/utils.py` — shared utilities (config loading, output comparison, file naming)
- `docs/PROGRESS.md` — append-only session log (see format below)
- `docs/SESSIONS.md` — upcoming session prompts

## Style

- Simple functions, no classes. This is an experiment, not a product.
- Subprocess calls to `llama-completion` for inference — no Python bindings.
- No external dependencies beyond stdlib + pyyaml + matplotlib.
- Fail loudly on errors. Never silently continue.
- No editorializing about the hypothesis in code comments.

## Progress Logging

After completing work, append a session entry to `docs/PROGRESS.md`. Use this format:

```
## Session [N]: [Title] - [Date]

### Completed
- What was accomplished

### Decisions
- Consequential choices with rationale (only if notable)

### Learnings
- Key discoveries (only if notable)

### Files
- Created: list
- Modified: list
```

Guidelines:
- ~15 lines max per session
- Focus on outcomes, not process
- Date format: YYYY-MM-DD
- Omit Decisions/Learnings sections if nothing notable
- Append only — never edit previous session entries

## Commit Format

```
implements Session [N]: [Title from PROGRESS.md]

why: [one-line rationale]
what: [one-line implementation summary]
status: complete
ref: docs/PROGRESS.md (Session [N], [YYYY-MM-DD])
```

Guidelines:
- Subject: lowercase "implements", capital "Session"
- `why`/`what` derived from the PROGRESS.md session entry
- Do not invent work not in the changeset
- If no PROGRESS entry exists yet, log progress before committing

## Hardware (big-pc)

- AMD Radeon RX 7700 XT (gfx1101, 12GB VRAM)
- ROCm 7.2.0, llama.cpp with HIP backend
- Model: llama-2-7b.Q4_0.gguf at ~/models/
- Binary: llama-completion (on PATH via ~/llama.cpp/build/bin/)
- Run scripts from the scripts/ directory
