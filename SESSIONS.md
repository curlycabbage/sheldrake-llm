# BIG-PC Session Prompts

Instructions for Claude Code on big-pc. Run these in order.

## Session 1: Clone and verify

```
Clone sheldrake-llm from GitHub. Update config/default.yaml:
- model path: ~/models/llama-2-7b.Q4_0.gguf
- llama_cli_path: llama-completion

Then run a single test inference to verify the setup works:
  cd scripts/
  python3 baseline.py --n-runs 1 --prompt-id light

If --log-disable causes an error, remove it from baseline.py's cmd list.
Check that the output JSON in data/baseline/ contains clean completion text
(no model-loading preamble mixed in). If stdout is polluted, we need to strip
the llama-completion preamble from the captured output.
```

## Session 2: Quick baseline smoke test

```
Run a small baseline to check for reproducibility before committing to 1000 runs:
  cd scripts/
  python3 baseline.py --n-runs 10 --prompt-id light

Report: are all 10 outputs identical? If yes, the noise floor may be zero —
great sensitivity for the experiment. If not, report how many diverged and
at which token.
```

## Session 3: Full baseline (Phase 2)

```
Run the full baseline characterization. Do this with nothing else running
on the machine — close browsers, games, anything GPU-intensive.

  cd scripts/
  python3 baseline.py --n-runs 100

This runs all 4 prompts x 100 runs each = 400 inferences.
At ~70 t/s with 256 max tokens, each run takes ~4 seconds.
Total: ~25 minutes.

After it completes, run:
  python3 analyze.py

Paste the summary output and commit the results.
```

## Session 4: Extended baseline (optional)

```
If Phase 2 shows zero variance (all outputs identical), run a longer baseline
to be sure:
  python3 baseline.py --n-runs 1000 --prompt-id light

If Phase 2 shows variance, skip this and move to characterizing the variance
patterns before running more.
```

## Notes

- Always run from the scripts/ directory
- Make sure pyyaml is installed: pip3 install pyyaml matplotlib
- The model path in config must be absolute or correct relative to scripts/
- If anything fails, paste the full error — don't try to fix it silently
