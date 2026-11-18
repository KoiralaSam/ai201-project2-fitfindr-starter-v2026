"""Three trials per fixed criterion, with real MCP outputs and append-only evidence."""
import argparse
import json
import os
from pathlib import Path
from capstone import search
from tools import search_listings

CANONICAL = ["tee on depop", "jacket on poshmark", "flannel on thredUp"]
VARIANTS = ["tee on DEPOP", "jacket ON POSHMARK", "flannel on thredup"]
PLATFORMS = ["depop", "poshmark", "thredUp"]


def ids(items):
    return [item["id"] for item in items]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    if not args.label.replace("-", "").replace("_", "").isalnum():
        parser.error("Use letters, numbers, hyphens or underscores for label.")
    root = Path("results") / ("capstone_" + args.label)
    root.mkdir(parents=True, exist_ok=False)
    log = root / "runs.jsonl"
    os.environ["FITFINDR_LOG"] = str(log)
    trials = []
    for trial in range(1, 4):
        cases = {str(n): [] for n in range(1, 6)}
        canonical = [search(query) for query in CANONICAL]
        for query, output, platform in zip(CANONICAL, canonical, PLATFORMS):
            cases["1"].append({"query": query, "output": output, "pass": bool(output["results"]) and all(x["platform"] == platform for x in output["results"])})
        for query, expected in zip(VARIANTS, canonical):
            output = search(query)
            cases["2"].append({"query": query, "output": output, "expected_ids": ids(expected["results"]), "pass": bool(expected["results"]) and ids(output["results"]) == ids(expected["results"])})
        for query in ["tee on ebay", "ballgown under $1 on depop"]:
            output = search(query)
            cases["3"].append({"query": query, "output": output, "pass": not output["results"] and "Change" in (output["error"] or "")})
        for keywords, budget, platform in [("graphic tee", 30, "depop"), ("jacket", 50, "poshmark"), ("flannel", 25, "thredUp")]:
            query = f"{keywords} under ${budget}"
            original = search(query)
            filtered = search(query + " on " + platform)
            expected = search_listings(keywords, max_price=budget)
            passed = ids(original["results"]) == ids(expected) and bool(filtered["results"]) and all(x["price"] <= budget and x["platform"] == platform for x in filtered["results"])
            cases["4"].append({"query": query, "output": filtered, "unfiltered": original, "expected_ids": ids(expected), "pass": passed})
        for query in ["tee on depop", "tee on ebay", ""]:
            before = log.read_text().splitlines()
            output = search(query)
            after = log.read_text().splitlines()
            record = json.loads(after[-1])
            previous_ids = {json.loads(line)["run_id"] for line in before}
            passed = len(after) == len(before) + 1 and record["input"] == query and record["output"] == output and record["duration_seconds"] >= 0 and record["timestamp"].endswith("+00:00") and record["run_id"] not in previous_ids and record["status"] == ("error" if output["error"] else "ok")
            cases["5"].append({"query": query, "output": record, "pass": passed})
        trials.append({"trial": trial, "criteria": cases})
        print(f"Trial {trial}: " + ", ".join(f"C{k}={sum(c['pass'] for c in v)}/{len(v)}" for k,v in cases.items()), flush=True)
    (root / "results.json").write_text(json.dumps(trials, indent=2) + "\n")
    lines = ["| Criterion | Target per trial | Run 1 | Run 2 | Run 3 | Verdict |", "|---|---|---|---|---|---|"]
    for key, target in [("1",3),("2",3),("3",2),("4",3),("5",3)]:
        counts = [sum(case["pass"] for case in trial["criteria"][key]) for trial in trials]
        lines.append(f"| {key} | {target}/{target} | " + " | ".join(f"{count}/{target}" for count in counts) + " | " + ("MET" if all(count == target for count in counts) else "MISSED") + " |")
    (root / "table.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
