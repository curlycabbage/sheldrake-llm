# Experimental Protocol

*Detailed procedure for all phases of the experiment. Follow this document step by step.*

## Phase 1: Environment Setup

### 1.1 WSL2 and Ubuntu

1. Enable WSL2 on Windows 11 host.
2. Install Ubuntu (22.04 LTS or later) from the Microsoft Store.
3. Update packages: `sudo apt update && sudo apt upgrade -y`

### 1.2 ROCm for AMD GPU

1. Follow AMD's official ROCm installation guide for WSL2.
2. Verify GPU is visible: `rocminfo | grep gfx1101`
3. Verify HIP is functional: `hipcc --version`

### 1.3 llama.cpp with ROCm Backend

1. Clone llama.cpp: `git clone https://github.com/ggerganov/llama.cpp.git`
2. Build with HIP/ROCm:
   ```bash
   cd llama.cpp
   cmake -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1101
   cmake --build build --config Release -j$(nproc)
   ```
3. Verify `llama-completion` is on PATH or note its absolute path for config.
4. Record the exact llama.cpp commit hash: `git rev-parse HEAD`

### 1.4 Model Download

1. Download the target model in GGUF format (e.g., from Hugging Face).
2. Place in a `models/` directory adjacent to the repo (not inside the repo — it's gitignored).
3. Record:
   - Exact filename
   - SHA256 hash: `sha256sum models/<filename>.gguf`
   - Source URL
   - Quantization format (Q4_0, Q4_K_M, etc.)
4. Update `config/default.yaml` with the correct model path and name.

### 1.5 Verification

1. Run a single inference manually:
   ```bash
   llama-completion -m ../models/llama-2-7b.Q4_0.gguf -p "Hello" -n 64 --seed 42 --temp 0 -ngl 99 --no-display-prompt --simple-io --no-perf
   ```
2. Confirm output is generated and GPU is being used (check `rocm-smi` during inference).
3. Run the same command twice and compare outputs to get an initial sense of determinism.

### 1.6 Version Documentation

Record the following in a session log before proceeding:
- Windows 11 build number
- WSL2 kernel version: `uname -r`
- Ubuntu version: `lsb_release -a`
- ROCm version: `apt show rocm-libs 2>/dev/null | grep Version`
- llama.cpp commit hash
- Model file, hash, and source
- GPU driver version: `rocm-smi --showdriverversion`

## Phase 2: Baseline Characterization

### 2.1 Purpose

Establish the mechanical noise floor: how much variance does the system produce with no changes to any parameter?

### 2.2 Procedure

1. Close all unnecessary applications on the Windows host.
2. Let the GPU reach thermal equilibrium (idle for 5 minutes).
3. Run the baseline script:
   ```bash
   cd scripts/
   python3 baseline.py
   ```
4. Default: 100 runs per prompt, seed=42, temperature=0, max_tokens=256.
5. For thorough characterization, increase to N=1000:
   ```bash
   python3 baseline.py --n-runs 1000
   ```

### 2.3 Thermal and Temporal Checks

1. Run a baseline batch in the morning and another in the evening.
2. Run a baseline batch after heavy GPU use (gaming, rendering) vs. cold start.
3. Compare results across these conditions to check for thermal/load effects.

### 2.4 Prompt Length Check

Run baselines with prompts of varying lengths to check if variance scales with generation length. The default config includes prompts of different complexity for this purpose.

### 2.5 Success Criteria

- If 100% of runs produce identical output: excellent. The noise floor is zero and even tiny operator effects would be detectable.
- If <100% identical: characterize the variance. Where do tokens first diverge? Is the divergence point consistent or random? What is the distribution of divergence points across runs?
- If variance is high and unpatterned: the experimental apparatus may lack the precision needed. Consider switching to CPU inference (fully deterministic but slower) or using a different model/quantization.

### 2.6 Outputs

- Individual run files in `data/baseline/`
- Summary statistics printed to console
- Record findings in `docs/RESULTS.md` Phase 2 section

## Phase 3: Operator Experiment

*Only proceed if Phase 2 produces a characterized baseline.*

### 3.1 Conditions

| Code | Condition | Description |
|------|-----------|-------------|
| A | Unattended | Machine runs alone, operator leaves the room |
| B | Operator A | Primary operator sits at keyboard, attending to machine |
| C | Operator B | Different person sits at keyboard, attending to machine |
| D | Distracted | Operator A sits at keyboard but is distracted (phone, etc.) |

### 3.2 Physical Setup

- Same chair, same distance from machine, same room.
- Room temperature noted at start of each session.
- No other people in the room (except in condition C).
- Machine and monitor in same state for all conditions (monitor on, same screen visible).

### 3.3 Procedure

1. Select a condition and prepare the physical setup.
2. Run the experiment script:
   ```bash
   cd scripts/
   python3 experiment.py --condition operator_a
   ```
3. Enter operator name and attention rating (1-5) when prompted.
4. The script runs N=100 inferences with identical parameters.
5. Repeat for each condition, randomizing order within sessions.

### 3.4 Session Design

- Run at least 2 sessions on different days.
- Within each session, run all 4 conditions in randomized order.
- Allow 5-minute GPU cool-down between conditions.
- Record session notes: anything unusual, interruptions, subjective observations.

### 3.5 Outputs

- Individual run files in `data/runs/`
- Each file includes condition, operator ID, attention rating, session notes.

## Phase 4: Analysis

### 4.1 Pre-Registration Discipline

Commit all analysis code (`scripts/analyze.py`) before examining experimental data. The analysis should be written to work on any data conforming to the expected JSON schema — do not peek at results and tailor analysis after the fact.

### 4.2 Procedure

1. Run the analysis script:
   ```bash
   cd scripts/
   python3 analyze.py
   ```
2. The script will:
   - Load all baseline and experiment runs
   - Compute identical output rates per condition
   - Perform token-level divergence analysis
   - Run statistical comparisons between conditions
   - Generate plots saved to `data/plots/`
   - Write detailed results to `docs/RESULTS.md`

### 4.3 Primary Metric

Rate of non-identical outputs per condition. If the baseline shows 0% variance and an operator condition shows >0% variance, that is immediately interesting.

### 4.4 Secondary Metrics

- Token-level divergence patterns: do different conditions produce different divergence signatures?
- Divergence point distributions: do outputs diverge earlier or later under different conditions?
- Correlation between operator attention rating and output properties.

### 4.5 Statistical Tests

The appropriate tests depend on baseline characterization:
- If baseline variance is zero: any operator-condition variance is significant by inspection (Fisher's exact test for proportion comparison).
- If baseline variance is non-zero: compare variance distributions using Mann-Whitney U test or Kolmogorov-Smirnov test, depending on distribution shape.
- For attention rating correlations: Spearman rank correlation.

### 4.6 Visualizations

- Bar chart: identical output rate by condition
- Histogram: divergence point distribution by condition
- Heatmap: token-level divergence patterns across runs

## Prompt Selection

The following prompts are configured in `config/default.yaml`:

| ID | Type | Prompt |
|----|------|--------|
| light | Factual | "What is the nature of light?" |
| silence | Creative | "Write a short paragraph about silence." |
| bridges | Reflective | "Explain why bridges are beautiful." |
| attention | Meta-cognitive | "What happens when you pay close attention to something?" |

These prompts were chosen to span different cognitive demands: factual recall, creative generation, aesthetic reflection, and meta-cognition. If the operator effect is real and related to attentional quality, different prompt types might show different effect sizes.
