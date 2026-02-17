# Progress Log

## Phase 1: Environment Setup

### Machine: big-pc (Eben's gaming PC)

**Hardware:**
- AMD Radeon RX 7700 XT (gfx1101, 12GB VRAM)
- Windows 11

**Software installed:**
- WSL2 with Ubuntu 24.04
- VS Code + WSL extension + Claude Code extension
- Git
- Python 3 (Windows + WSL)
- Claude Code (installed in WSL, authenticated)

**ROCm:**
- ROCm 7.2.0 installed via `amdgpu-install --usecase=wsl,rocm --no-dkms`
- HIP version: 7.2.26015-fc0010cf6a
- AMD clang version: 22.0.0 (roc-7.2)
- GPU confirmed: `rocminfo | grep gfx1101` shows device

**llama.cpp:**
- Cloned and built with HIP/ROCm backend
- Commit: `05fa625eac5bbdbe88b43f857156c35501421d6e`
- CMake flags: `-DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1101`
- Binary location: `~/llama.cpp/build/bin/llama-cli` (added to PATH)
- GPU detected on launch: `AMD Radeon RX 7700 XT, gfx1101 (0x1101), Wave Size: 32`

**Windows driver:**
- AMD Adrenalin 26.1.1 (updated 2026-02-16)

**Model:**
- llama-2-7b.Q4_0.gguf (3.83GB) from TheBloke/Llama-2-7B-GGUF
- Location: `~/models/llama-2-7b.Q4_0.gguf`
- Verified working: 73.0 t/s generation, 284.2 t/s prompt processing

**Phase 1 status: COMPLETE**

## Session 1: Clone and verify - 2026-02-16

### Completed
- Updated `config/default.yaml`: absolute model path, llama_cli_path confirmed as `llama-completion`
- Fixed `baseline.py` output capture: replaced `--log-disable` with `--no-display-prompt --simple-io --no-perf`
- Ran single test inference (`--n-runs 1 --prompt-id light`): clean completion text in output JSON

### Learnings
- `llama-completion --log-disable` suppresses completion output along with logs; `--simple-io --no-display-prompt` gives clean stdout
- Installed pyyaml + matplotlib via `pip3 install --break-system-packages`

### Files
- Modified: `config/default.yaml`, `scripts/baseline.py`

## Session 2: Quick baseline smoke test - 2026-02-16

### Completed
- Ran 10 inferences with prompt "light" (seed=42, temp=0, 256 max tokens)
- Result: **10/10 identical** — noise floor is zero
- ~7s per run (~70 t/s generation)

### Files
- Created: 10 JSON files in `data/baseline/`

## Session 3: Variance detection validation - 2026-02-16

### Completed
- Created `variance_check.py` to confirm detection system catches real variance
- Initial run (same seed, temp=0.8): all identical — revealed that fixed seed makes even temp>0 deterministic
- Fixed: vary seed per run (42, 43, 44...); rerun showed 10 unique outputs from 10 runs
- Added determinism model section (2.2) to PROTOCOL.md explaining both layers of determinism
- Fixed misleading output text ("9 of 10 diverged" → "10 unique outputs from 10 runs")

### Learnings
- Fixed seed + any temperature = deterministic output; variance requires both temp>0 AND varying seeds
- `compare_outputs` always counts run 0 as "identical" (compared to itself)

### Files
- Created: `scripts/variance_check.py`
- Modified: `scripts/baseline.py` (seed override param), `docs/PROTOCOL.md`

## Phase 2: Baseline Characterization

Not yet started.

## Phase 3: Operator Experiment

Not yet started.

## Phase 4: Analysis

Not yet started.
