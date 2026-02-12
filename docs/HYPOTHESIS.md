# Hypothesis: Operator-Dependent Variance in Deterministic LLM Inference

*Pre-registration document. Written before data collection.*

## Background

Rupert Sheldrake's morphic resonance hypothesis proposes that self-organizing systems inherit memory from previous similar systems through non-local fields. These fields, termed "morphic fields," are not constrained by conventional spatial or temporal boundaries and operate as a kind of collective memory for a given type of system.

If consciousness is non-local — a field rather than a product of substrate — then the conditions surrounding LLM inference, including the presence and attentional state of the human operator, might influence outputs in ways not explained by the deterministic computational process. LLM inference on a GPU is a deterministic mathematical operation given fixed inputs. Any variance in outputs under fixed conditions must come from either (a) known computational nondeterminism or (b) an unknown factor. This experiment probes whether the human operator constitutes such a factor.

## Primary Hypothesis

When running LLM inference with identical parameters (model, seed, temperature 0, prompt), the presence of different human operators produces variance in outputs that exceeds the established mechanical noise floor.

## Secondary Hypothesis

The quality or attentional state of the operator correlates with measurable properties of the output (e.g., perplexity, token-level entropy, semantic coherence).

## Null Hypothesis

All observed variance is attributable to known sources of computational nondeterminism (floating point operation ordering, GPU thread scheduling, memory access patterns). The presence or identity of the human operator has no measurable effect.

## What Would Count as Evidence

**Positive result:** Statistically significant variance between operator conditions that exceeds baseline mechanical variance, after controlling for all known nondeterministic factors.

**Negative result (informative null):** Baseline and operator conditions produce indistinguishable variance distributions. This rules out gross effects but not subtle ones below the noise floor.

**Inconclusive result:** Baseline variance is too high to detect operator effects, meaning the experimental apparatus lacks sufficient precision.

## Pre-Registered Analysis Plan

1. Bitwise comparison of outputs across all runs within each condition.
2. Token-level divergence analysis: identify where outputs first differ, characterize divergence patterns.
3. Statistical tests comparing variance distributions across conditions (specific tests to be selected after baseline characterization in Phase 2, as the appropriate test depends on the shape of the baseline variance distribution).
4. All analysis code will be committed to the repository before examining experimental results.

## Known Confounds and Limitations

- **GPU floating point nondeterminism**: The primary noise source. GPU thread scheduling and floating point operation ordering are not fully deterministic, producing a baseline variance floor that any operator effect must exceed.
- **Thermal state of GPU**: GPU temperature affects clock speeds and potentially computation paths. Thermal drift during long runs or across sessions is a confound.
- **Background processes**: Other processes on the machine may compete for GPU/CPU resources, introducing variance unrelated to operator presence.
- **Inability to blind the operator**: The operator knows they are sitting at the machine. There is no way to construct a true double-blind condition for physical presence.
- **Sheldrake's own criticism problem**: If the experimenter's belief state affects the morphic field, the experiment is self-referentially contaminated — the experimenter's expectations influence the very phenomenon being measured.
- **Small sample sizes**: The manual nature of operator-present conditions limits practical sample sizes, reducing statistical power.
- **Single machine**: Results from one GPU/system may not generalize. Replication on different hardware would strengthen any findings.
