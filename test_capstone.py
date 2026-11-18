"""Focused integration boundaries not covered by the real-MCP acceptance trials."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from agent import parse_query, run_agent
from capstone import search
from tools import search_listings


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.log = Path(self.directory.name) / "runs.jsonl"
        self.environment = patch.dict(os.environ, {"FITFINDR_LOG": str(self.log)})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.directory.cleanup()

    def test_agent_passes_platform_and_same_item_to_generation(self):
        item = search_listings("tee", platform="depop")[0]
        with patch("agent.mcp_client.call_tool", return_value=[item]) as mcp, patch("agent.suggest_outfit", return_value="outfit") as outfit, patch("agent.create_fit_card", return_value="caption") as card:
            result = run_agent("tee under $30 on DEPOP", {"items": []})
        self.assertEqual(mcp.call_args.args[1]["platform"], "DEPOP")
        self.assertEqual(mcp.call_args.args[1]["description"], "tee")
        outfit.assert_called_once_with(item, {"items": []})
        card.assert_called_once_with("outfit", item)
        self.assertEqual(result["fit_card"], "caption")
        self.assertEqual(json.loads(self.log.read_text())["status"], "ok")

    def test_transport_failure_is_recorded_before_propagating(self):
        with patch("capstone.call_tool", side_effect=RuntimeError("controlled transport failure")):
            with self.assertRaisesRegex(RuntimeError, "controlled transport failure"):
                search("tee on depop")
        record = json.loads(self.log.read_text())
        self.assertEqual(record["status"], "error")
        self.assertEqual(record["output"]["error"], "controlled transport failure")

    def test_platform_is_optional_and_applied_before_limit(self):
        self.assertIsNone(parse_query("platform sneakers")["platform"])
        results = search_listings("jacket", platform=" POSHMARK ")
        self.assertTrue(results)
        self.assertTrue(all(item["platform"] == "poshmark" for item in results))


if __name__ == "__main__":
    unittest.main()
