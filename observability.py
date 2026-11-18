"""Append-only local JSONL records shared by the search CLI and full agent."""
import functools
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


def logged(operation):
    def decorate(function):
        @functools.wraps(function)
        def wrapped(query, *args, **kwargs):
            started = time.perf_counter()
            record = {
                "run_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "operation": operation, "input": query,
            }
            try:
                output = function(query, *args, **kwargs)
                record.update(output=output, status="error" if output.get("error") else "ok")
                return output
            except Exception as exc:
                record.update(output={"error": str(exc)}, status="error")
                raise
            finally:
                record["duration_seconds"] = time.perf_counter() - started
                path = Path(os.environ.get("FITFINDR_LOG", "logs/runs.jsonl"))
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return wrapped
    return decorate
