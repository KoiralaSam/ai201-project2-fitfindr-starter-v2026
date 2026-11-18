"""Measure ten real local search runs; elapsed seconds include MCP startup."""
import json
import os
import statistics
from pathlib import Path
from capstone import search

if __name__ == "__main__":
    destination = Path("results/capstone_cost.jsonl")
    if destination.exists():
        raise SystemExit("Cost evidence already exists; move it before a new measurement.")
    os.environ["FITFINDR_LOG"] = str(destination)
    for index in range(10):
        output = search("graphic tee under $30 on depop")
        if output["error"]:
            raise SystemExit(output["error"])
        print(f"Measured run {index + 1}/10", flush=True)
    records = [json.loads(line) for line in destination.read_text().splitlines()]
    durations = [record["duration_seconds"] for record in records]
    summary = {
        "runs": len(records), "metric": "elapsed wall-clock seconds, including MCP process startup",
        "mean_seconds": statistics.mean(durations),
        "min_seconds": min(durations), "max_seconds": max(durations),
        "seconds_for_100_searches": sum(durations) * 10,
        "model_calls_per_search": 0,
        "scope": "search extension only; excludes Gemini outfit/caption calls",
    }
    Path("results/capstone_cost_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
