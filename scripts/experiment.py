"""Run operator experiment: inference under different operator conditions."""

import argparse
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

# Reuse the inference function from baseline
from baseline import run_inference

DATA_DIR = Path(__file__).parent.parent / "data" / "runs"

VALID_CONDITIONS = ["unattended", "operator_a", "operator_b", "distracted"]


def get_operator_info(condition):
    """Prompt the user for operator metadata before a batch."""
    if condition == "unattended":
        return {
            "operator": "none",
            "attention_rating": None,
            "session_notes": "",
        }

    print(f"\n--- Condition: {condition} ---")
    operator = input("Operator name: ").strip()
    if not operator:
        print("Error: operator name is required.")
        sys.exit(1)

    while True:
        try:
            rating = int(input("Attention rating (1-5): ").strip())
            if 1 <= rating <= 5:
                break
            print("Must be between 1 and 5.")
        except ValueError:
            print("Must be an integer.")

    notes = input("Session notes (optional, press Enter to skip): ").strip()

    return {
        "operator": operator,
        "attention_rating": rating,
        "session_notes": notes,
    }


def run_experiment(config, prompt, condition, operator_info, n_runs, log):
    """Run N inferences for a single prompt under a given condition."""
    prompt_id = prompt["id"]
    prompt_text = prompt["text"]
    seed = config["inference"]["seed"]
    runs = []

    log.info(
        "Condition '%s', prompt '%s': running %d inferences",
        condition, prompt_id, n_runs,
    )

    for i in range(n_runs):
        ts = timestamp_now()
        log.info("  Run %d/%d", i + 1, n_runs)

        output = run_inference(config, prompt_text)

        filename = make_run_filename(
            "experiment", seed, i, ts,
            prompt_id=prompt_id, condition=condition,
        )
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
            "condition": condition,
            "operator": operator_info["operator"],
            "attention_rating": operator_info["attention_rating"],
            "session_notes": operator_info["session_notes"],
        }

        save_run(run_data, DATA_DIR)
        runs.append(run_data)

    return runs


def main():
    parser = argparse.ArgumentParser(description="Run operator experiment")
    parser.add_argument(
        "--condition", required=True, choices=VALID_CONDITIONS,
        help="Experimental condition",
    )
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    parser.add_argument("--n-runs", type=int, default=None, help="Override number of runs")
    parser.add_argument("--prompt-id", type=str, default=None, help="Run only this prompt")
    args = parser.parse_args()

    log = setup_logging()
    config = load_config(args.config)
    n_runs = args.n_runs or config["experiment"]["n_runs"]

    prompts = config["prompts"]
    if args.prompt_id:
        prompts = [p for p in prompts if p["id"] == args.prompt_id]
        if not prompts:
            log.error("Prompt ID '%s' not found in config", args.prompt_id)
            sys.exit(1)

    operator_info = get_operator_info(args.condition)

    for prompt in prompts:
        runs = run_experiment(config, prompt, args.condition, operator_info, n_runs, log)
        stats = compare_outputs(runs)

        total = stats["total"]
        identical = stats["identical"]
        print(f"\n--- {args.condition} / {prompt['id']} ---")
        print(f"{identical} of {total} runs produced identical output.")

    print("\nExperiment complete. Results saved to", DATA_DIR)


if __name__ == "__main__":
    main()
