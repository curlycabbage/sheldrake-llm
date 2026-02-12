import hashlib
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def load_config(config_path=None):
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config" / "default.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def resolve_model_path(config):
    """Resolve model path relative to the scripts directory."""
    model_path = config["model"]["path"]
    if not os.path.isabs(model_path):
        model_path = str(Path(__file__).parent / model_path)
    return os.path.normpath(model_path)


def make_run_filename(prefix, seed, run_index, timestamp, prompt_id=None, condition=None):
    """Generate a filename following the project naming convention."""
    parts = []
    if condition:
        parts.append(condition)
    else:
        parts.append(prefix)
    if prompt_id:
        parts.append(prompt_id)
    parts.append(str(seed))
    parts.append(str(run_index))
    parts.append(timestamp.replace(":", "-").replace(" ", "_"))
    return "_".join(parts) + ".json"


def save_run(data, directory):
    """Save a run's data as JSON."""
    os.makedirs(directory, exist_ok=True)
    filename = data.get("filename")
    if not filename:
        raise ValueError("Run data must include a 'filename' key")
    filepath = os.path.join(directory, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath


def load_runs(directory):
    """Load all JSON run files from a directory."""
    runs = []
    directory = Path(directory)
    if not directory.exists():
        return runs
    for filepath in sorted(directory.glob("*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            runs.append(json.load(f))
    return runs


def compare_outputs(runs):
    """Compare outputs across runs. Returns stats about identical/divergent runs.

    Returns a dict with:
      - total: number of runs
      - identical: number of runs identical to the first
      - divergent: list of (run_index, first_divergence_token) for non-identical runs
    """
    if not runs:
        return {"total": 0, "identical": 0, "divergent": []}

    reference = runs[0]["output"]
    ref_tokens = reference.split()
    identical = 0
    divergent = []

    for run in runs:
        output = run["output"]
        if output == reference:
            identical += 1
        else:
            # Find first divergent token
            tokens = output.split()
            first_diff = None
            for i, (a, b) in enumerate(zip(ref_tokens, tokens)):
                if a != b:
                    first_diff = i
                    break
            if first_diff is None:
                # One is a prefix of the other
                first_diff = min(len(ref_tokens), len(tokens))
            divergent.append({
                "run_index": run["run_index"],
                "first_divergence_token": first_diff,
            })

    return {
        "total": len(runs),
        "identical": identical,
        "divergent": divergent,
    }


def bitwise_compare(a, b):
    """Compare two strings byte-by-byte. Returns index of first difference, or -1 if identical."""
    min_len = min(len(a), len(b))
    for i in range(min_len):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return min_len
    return -1


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
    )
    return logging.getLogger("sheldrake")


def timestamp_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
