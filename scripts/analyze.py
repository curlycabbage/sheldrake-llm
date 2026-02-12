"""Analyze baseline and experiment data. Compare variance across conditions."""

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from utils import (
    bitwise_compare,
    compare_outputs,
    load_config,
    load_runs,
    setup_logging,
)

BASELINE_DIR = Path(__file__).parent.parent / "data" / "baseline"
RUNS_DIR = Path(__file__).parent.parent / "data" / "runs"
PLOTS_DIR = Path(__file__).parent.parent / "data" / "plots"
RESULTS_PATH = Path(__file__).parent.parent / "docs" / "RESULTS.md"


def group_by_prompt(runs):
    """Group runs by prompt_id."""
    grouped = defaultdict(list)
    for run in runs:
        grouped[run["prompt_id"]].append(run)
    return dict(grouped)


def group_by_condition(runs):
    """Group runs by condition."""
    grouped = defaultdict(list)
    for run in runs:
        grouped[run.get("condition", "baseline")].append(run)
    return dict(grouped)


def analyze_baseline(log):
    """Analyze baseline runs and return results."""
    runs = load_runs(BASELINE_DIR)
    if not runs:
        log.warning("No baseline data found in %s", BASELINE_DIR)
        return None

    log.info("Loaded %d baseline runs", len(runs))
    by_prompt = group_by_prompt(runs)
    results = {}

    for prompt_id, prompt_runs in sorted(by_prompt.items()):
        stats = compare_outputs(prompt_runs)
        results[prompt_id] = stats
        log.info(
            "  Prompt '%s': %d/%d identical",
            prompt_id, stats["identical"], stats["total"],
        )

    return results


def analyze_experiment(log):
    """Analyze experiment runs and return results grouped by condition and prompt."""
    runs = load_runs(RUNS_DIR)
    if not runs:
        log.warning("No experiment data found in %s", RUNS_DIR)
        return None

    log.info("Loaded %d experiment runs", len(runs))
    by_condition = group_by_condition(runs)
    results = {}

    for condition, cond_runs in sorted(by_condition.items()):
        by_prompt = group_by_prompt(cond_runs)
        results[condition] = {}
        for prompt_id, prompt_runs in sorted(by_prompt.items()):
            stats = compare_outputs(prompt_runs)
            results[condition][prompt_id] = stats
            log.info(
                "  %s / %s: %d/%d identical",
                condition, prompt_id, stats["identical"], stats["total"],
            )

    return results


def plot_identical_rates(baseline_results, experiment_results):
    """Bar chart: identical output rate by condition for each prompt."""
    os.makedirs(PLOTS_DIR, exist_ok=True)

    # Collect all prompt IDs
    prompt_ids = set()
    if baseline_results:
        prompt_ids.update(baseline_results.keys())
    if experiment_results:
        for cond_data in experiment_results.values():
            prompt_ids.update(cond_data.keys())
    prompt_ids = sorted(prompt_ids)

    if not prompt_ids:
        return

    # Build data: condition -> prompt -> identical rate
    conditions = []
    if baseline_results:
        conditions.append("baseline")
    if experiment_results:
        conditions.extend(sorted(experiment_results.keys()))

    for prompt_id in prompt_ids:
        rates = []
        labels = []
        for cond in conditions:
            if cond == "baseline":
                stats = baseline_results.get(prompt_id)
            else:
                stats = experiment_results.get(cond, {}).get(prompt_id)
            if stats and stats["total"] > 0:
                rates.append(stats["identical"] / stats["total"] * 100)
                labels.append(cond)

        if not rates:
            continue

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(labels, rates)
        ax.set_ylabel("Identical Output Rate (%)")
        ax.set_title(f"Identical Output Rate by Condition — Prompt: {prompt_id}")
        ax.set_ylim(0, 105)
        for i, v in enumerate(rates):
            ax.text(i, v + 1, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / f"identical_rate_{prompt_id}.png", dpi=150)
        plt.close()


def plot_divergence_distribution(baseline_results, experiment_results):
    """Histogram: divergence point distribution by condition."""
    os.makedirs(PLOTS_DIR, exist_ok=True)

    all_data = {}
    if baseline_results:
        for prompt_id, stats in baseline_results.items():
            if stats["divergent"]:
                key = f"baseline/{prompt_id}"
                all_data[key] = [d["first_divergence_token"] for d in stats["divergent"]]

    if experiment_results:
        for cond, cond_data in experiment_results.items():
            for prompt_id, stats in cond_data.items():
                if stats["divergent"]:
                    key = f"{cond}/{prompt_id}"
                    all_data[key] = [d["first_divergence_token"] for d in stats["divergent"]]

    if not all_data:
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    for label, tokens in sorted(all_data.items()):
        ax.hist(tokens, bins=20, alpha=0.5, label=label)
    ax.set_xlabel("First Divergent Token Index")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of First Divergence Points")
    ax.legend()
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "divergence_distribution.png", dpi=150)
    plt.close()


def write_results(baseline_results, experiment_results):
    """Write analysis results to docs/RESULTS.md."""
    lines = ["# Results\n"]

    # Phase 2
    lines.append("## Phase 2: Baseline Results\n")
    if baseline_results:
        for prompt_id, stats in sorted(baseline_results.items()):
            total = stats["total"]
            identical = stats["identical"]
            pct = identical / total * 100 if total > 0 else 0
            lines.append(f"### Prompt: {prompt_id}\n")
            lines.append(f"- Runs: {total}")
            lines.append(f"- Identical outputs: {identical} ({pct:.1f}%)")
            if stats["divergent"]:
                tokens = [d["first_divergence_token"] for d in stats["divergent"]]
                lines.append(f"- Divergent runs: {len(stats['divergent'])}")
                lines.append(f"- First divergence token: min={min(tokens)}, max={max(tokens)}, mean={sum(tokens)/len(tokens):.1f}")
            lines.append("")
    else:
        lines.append("Not yet run.\n")

    # Phase 3
    lines.append("## Phase 3: Operator Results\n")
    if experiment_results:
        for condition, cond_data in sorted(experiment_results.items()):
            lines.append(f"### Condition: {condition}\n")
            for prompt_id, stats in sorted(cond_data.items()):
                total = stats["total"]
                identical = stats["identical"]
                pct = identical / total * 100 if total > 0 else 0
                lines.append(f"**Prompt: {prompt_id}**")
                lines.append(f"- Runs: {total}")
                lines.append(f"- Identical outputs: {identical} ({pct:.1f}%)")
                if stats["divergent"]:
                    tokens = [d["first_divergence_token"] for d in stats["divergent"]]
                    lines.append(f"- Divergent runs: {len(stats['divergent'])}")
                    lines.append(f"- First divergence token: min={min(tokens)}, max={max(tokens)}, mean={sum(tokens)/len(tokens):.1f}")
                lines.append("")
    else:
        lines.append("Not yet run.\n")

    # Phase 4
    lines.append("## Phase 4: Analysis\n")
    if baseline_results and experiment_results:
        lines.append("See plots in `data/plots/` for visualizations.\n")
        lines.append("Statistical comparison between conditions requires manual review of the generated plots and the summary data above.\n")
    else:
        lines.append("Not yet run.\n")

    # Conclusions
    lines.append("## Conclusions\n")
    lines.append("Not yet run.\n")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def print_summary(baseline_results, experiment_results):
    """Print a console summary."""
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)

    if baseline_results:
        print("\nBASELINE:")
        for prompt_id, stats in sorted(baseline_results.items()):
            total = stats["total"]
            identical = stats["identical"]
            pct = identical / total * 100 if total > 0 else 0
            print(f"  {prompt_id}: {identical}/{total} identical ({pct:.1f}%)")
    else:
        print("\nBASELINE: No data")

    if experiment_results:
        print("\nEXPERIMENT:")
        for condition, cond_data in sorted(experiment_results.items()):
            print(f"\n  Condition: {condition}")
            for prompt_id, stats in sorted(cond_data.items()):
                total = stats["total"]
                identical = stats["identical"]
                pct = identical / total * 100 if total > 0 else 0
                print(f"    {prompt_id}: {identical}/{total} identical ({pct:.1f}%)")
    else:
        print("\nEXPERIMENT: No data")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Analyze experiment data")
    parser.add_argument("--config", type=str, default=None, help="Path to config YAML")
    args = parser.parse_args()

    log = setup_logging()

    baseline_results = analyze_baseline(log)
    experiment_results = analyze_experiment(log)

    if not baseline_results and not experiment_results:
        log.error("No data found. Run baseline.py or experiment.py first.")
        sys.exit(1)

    plot_identical_rates(baseline_results, experiment_results)
    plot_divergence_distribution(baseline_results, experiment_results)
    write_results(baseline_results, experiment_results)
    print_summary(baseline_results, experiment_results)

    print(f"\nResults written to {RESULTS_PATH}")
    print(f"Plots saved to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
