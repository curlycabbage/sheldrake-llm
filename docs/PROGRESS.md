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
- Not yet downloaded

## Phase 2: Baseline Characterization

Not yet started.

## Phase 3: Operator Experiment

Not yet started.

## Phase 4: Analysis

Not yet started.
