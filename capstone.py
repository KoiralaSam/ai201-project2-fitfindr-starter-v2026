"""Local platform-search run path; uses the original parser and actual MCP transport."""
import argparse
import json
from agent import parse_query
from mcp_client import call_tool
from observability import logged


@logged("search")
def search(query):
    if not isinstance(query, str) or not query.strip():
        return {"results": [], "error": "Enter keywords and optionally 'on depop', 'on poshmark', or 'on thredUp'."}
    parsed = parse_query(query)
    results = call_tool("search_listings", parsed)
    return {
        "parsed": parsed, "results": results,
        "error": None if results else "No matches. Change the keywords, budget, size, or platform (depop, poshmark, thredUp).",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    args = parser.parse_args()
    result = search(args.query)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result["error"] is None else 1)
