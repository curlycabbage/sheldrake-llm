"""Sanity check: confirm the system detects variance when temperature > 0.

Runs a small batch with temp=0.8 and verifies that outputs diverge.
This validates that our comparison logic works and that temp=0 determinism
is real, not an artifact of broken output capture.

Results are saved to data/variance_check/ and not mixed with baseline data.
"""

import argparse
import sys
from pathlib import Path

from baseline import run_inference, print_summary
from utils import (
    compare_outputs,
    load_config,
    make_run_filename,
    save_run,
    setup_logging,
    timestamp_now,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "variance_check"


def main():
    parser = argparse.ArgumentParser(description="Variance detection sanity check")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--n-runs", type=int, default=10, help="Number of runs (default: 10)")
    parser.add_argument("--temp", type=float, default=0.8, help="Temperature (default: 0.8)")
    parser.add_argument("--prompt-id", type=str, default="light", help="Prompt to use (default: light)")
    args = parser.parse_args()

    log = setup_logging()
    config = load_config(args.config)

    # Override temperature
    original_temp = config["inference"]["temperature"]
    config["inference"]["temperature"] = args.temp

    prompts = [p for p in config["prompts"] if p["id"] == args.prompt_id]
    if not prompts:
        log.error("Prompt ID '%s' not found in config", args.prompt_id)
        sys.exit(1)

    prompt = prompts[0]
    base_seed = config["inference"]["seed"]
    runs = []

    log.info("Variance check: %d runs, temp=%.1f, prompt='%s' (varying seeds)", args.n_runs, args.temp, args.prompt_id)

    for i in range(args.n_runs):
        ts = timestamp_now()
        seed = base_seed + i
        log.info("  Run %d/%d (seed=%d)", i + 1, args.n_runs, seed)

        output = run_inference(config, prompt["text"], seed=seed)

        filename = make_run_filename("varcheck", seed, i, ts, prompt_id=args.prompt_id)
        run_data = {
            "filename": filename,
            "run_index": i,
            "seed": seed,
            "temperature": args.temp,
            "prompt_id": args.prompt_id,
            "prompt": prompt["text"],
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

    stats = compare_outputs(runs)
    print_summary(args.prompt_id, stats)

    # compare_outputs counts the reference run (run 0) as "identical" to itself,
    # so N-1 divergent out of N total means all runs produced unique output.
    n_unique = len(stats["divergent"]) + 1  # +1 for the reference run itself
    if stats["divergent"]:
        print(f"\n{n_unique} unique outputs from {stats['total']} runs.")
        print("Detection system is working correctly.")
    else:
        print(f"\nWARNING: All {stats['total']} runs were identical at temp={args.temp}.")
        print("This is unexpected and may indicate a problem.")

    print("\nResults saved to", DATA_DIR)


if __name__ == "__main__":
    main()
