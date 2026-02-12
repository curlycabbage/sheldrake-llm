# sheldrake-llm

Experimental framework for testing whether the presence of a human operator affects the output of deterministic LLM inference.

The core question: when running the same model with identical parameters (seed, temperature, prompt), does the presence of different human operators produce measurable variance in outputs that exceeds the mechanical noise floor?

See [HYPOTHESIS.md](docs/HYPOTHESIS.md) for the full pre-registration and [PROTOCOL.md](docs/PROTOCOL.md) for the experimental procedure.

## Hardware Requirements

- AMD GPU with ROCm support (tested on RX 7700 XT, RDNA3/gfx1101, 12GB VRAM)
- Windows 11 with WSL2 (Ubuntu)
- ~8GB disk space for a 7B Q4 model

## Setup

### 1. WSL2 + ROCm

Install WSL2 with Ubuntu, then install ROCm following AMD's official guide. Verify with:

```bash
rocminfo | grep gfx1101
```

### 2. llama.cpp

Build llama.cpp with the ROCm/HIP backend:

```bash
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1101
cmake --build build --config Release -j$(nproc)
```

Ensure `llama-cli` is on your PATH, or update `config/default.yaml` with the full path.

### 3. Model

Download a GGUF model (e.g., Llama 2 7B Q4_0 or Mistral 7B Q4_K_M) and place it in a `models/` directory next to this repo:

```
parent/
  models/
    llama-2-7b.Q4_0.gguf
  sheldrake-llm/
    ...
```

Update `config/default.yaml` with the correct model path and name.

### 4. Python Dependencies

```bash
pip install pyyaml matplotlib
```

No other external dependencies.

## Usage

### Baseline (Phase 2)

Establish the mechanical noise floor by running N identical inferences:

```bash
cd scripts/
python baseline.py                  # 100 runs (default)
python baseline.py --n-runs 1000    # thorough characterization
python baseline.py --prompt-id light  # single prompt only
```

Results are saved to `data/baseline/`.

### Experiment (Phase 3)

Run inference under different operator conditions:

```bash
cd scripts/
python experiment.py --condition unattended
python experiment.py --condition operator_a
python experiment.py --condition operator_b
python experiment.py --condition distracted
```

You'll be prompted for operator name and attention rating. Results are saved to `data/runs/`.

### Analysis (Phase 4)

Compare variance across conditions:

```bash
cd scripts/
python analyze.py
```

Outputs a summary to the console, writes detailed results to `docs/RESULTS.md`, and generates plots in `data/plots/`.

## Project Structure

```
sheldrake-llm/
  README.md
  docs/
    HYPOTHESIS.md       # Pre-registration document
    PROTOCOL.md         # Detailed experimental procedure
    RESULTS.md          # Findings (populated by analyze.py)
  scripts/
    baseline.py         # Phase 2: baseline characterization
    experiment.py       # Phase 3: operator experiment
    analyze.py          # Phase 4: analysis and visualization
    utils.py            # Shared utilities
  data/
    baseline/           # Baseline run data (gitignored)
    runs/               # Experiment run data (gitignored)
  config/
    default.yaml        # All configurable parameters
```
