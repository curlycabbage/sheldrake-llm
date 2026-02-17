"""Run baseline characterization: N identical inferences to establish the mechanical noise floor."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from utils import (
    compare_outputs,
    load_config,
    make_run_filename,
    resolve_model_path,
    save_run,
    setup_logging,
    timestamp_now,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "baseline"


def run_inference(config, prompt_text):
    """Run a single inference via llama-completion and return the output text."""
    model_path = resolve_model_path(config)
    inf = config["inference"]

    cmd = [
        inf["llama_cli_path"],
        "-m", model_path,
        "-p", prompt_text,
        "-n", str(inf["max_tokens"]),
        "--seed", str(inf["seed"]),
        "--temp", str(inf["temperature"]),
        "-ngl", str(inf["n_gpu_layers"]),
        "--no-display-prompt",
        "--simple-io",
        "--no-perf",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"llama-completion failed (exit {result.returncode}):\n{result.stderr}"
        )

    return result.stdout


def run_baseline(config, prompt, n_runs, log):
    """Run N inferences for a single prompt and save results."""
    prompt_id = prompt["id"]
    prompt_text = prompt["text"]
    seed = config["inference"]["seed"]
    runs = []

    log.info("Prompt '%s': running %d inferences", prompt_id, n_runs)

    for i in range(n_runs):
        ts = timestamp_now()
        log.info("  Run %d/%d", i + 1, n_runs)

        output = run_inference(config, prompt_text)

        filename = make_run_filename("baseline", seed, i, ts, prompt_id=prompt_id)
        run_data = {
            "filename": filename,
            "run_index": i,
            "seed": seed,
            "temperature": config["inference"]["temperature"],
            "prompt_id": prompt_id,
            "prompt": prompt_text,
            "output": output,
            "timestamp": ts,
            "model": config["model"]["name"],
            "params": {
                "max_tokens": config["inference"]["max_tokens"],
                "n_gpu_layers": config["inference"]["n_gpu_layers"],
            },
        }

        save_run(run_data, DATA_DIR)
        runs.append(run_data)

    return runs


def print_summary(prompt_id, stats):
    """Print a human-readable summary of the comparison."""
    total = stats["total"]
    identical = stats["identical"]
    divergent = stats["divergent"]

    print(f"\n--- Prompt: {prompt_id} ---")
    print(f"{identical} of {total} runs produced identical output.")

    if divergent:
        tokens = [d["first_divergence_token"] for d in divergent]
        min_t = min(tokens)
        max_t = max(tokens)
        avg_t = sum(tokens) / len(tokens)
        print(
            f"First divergence at token {min_t}-{max_t} "
            f"(avg {avg_t:.1f}) in {len(divergent)} runs."
        )


def main():
    parser = argparse.ArgumentParser(description="Run baseline characterization")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--n-runs", type=int, default=None, help="Override number of runs")
    parser.add_argument("--prompt-id", type=str, default=None, help="Run only this prompt")
    args = parser.parse_args()

    log = setup_logging()
    config = load_config(args.config)
    n_runs = args.n_runs or config["baseline"]["n_runs"]

    prompts = config["prompts"]
    if args.prompt_id:
        prompts = [p for p in prompts if p["id"] == args.prompt_id]
        if not prompts:
            log.error("Prompt ID '%s' not found in config", args.prompt_id)
            sys.exit(1)

    for prompt in prompts:
        runs = run_baseline(config, prompt, n_runs, log)
        stats = compare_outputs(runs)
        print_summary(prompt["id"], stats)

    print("\nBaseline complete. Results saved to", DATA_DIR)


if __name__ == "__main__":
    main()
