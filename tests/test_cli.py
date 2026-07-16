from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from xnb.cli import audit_draft, main
from xnb.registry import CURRENT_UPSTREAM_COMMIT, RegistryError, load_registry


def _claim(claim_id: str, claim: str, verdict: str) -> dict[str, object]:
    return {
        "id": claim_id,
        "claim": claim,
        "verdict": verdict,
        "practical_implication": "Test instead of assuming.",
        "evidence_summary": "Fixture evidence.",
        "upstream_commit": CURRENT_UPSTREAM_COMMIT,
        "sources": [
            {
                "repository": "xai-org/x-algorithm",
                "commit": CURRENT_UPSTREAM_COMMIT,
                "path": "README.md",
                "line_start": 1,
                "line_end": 2,
                "url": f"https://github.com/xai-org/x-algorithm/blob/{CURRENT_UPSTREAM_COMMIT}/README.md#L1-L2",
            }
        ],
    }


def _registry(claims: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": "1.0.0",
        "registry_version": "0.1.0",
        "reviewed_at": "2026-07-16",
        "upstream": {
            "repository": "xai-org/x-algorithm",
            "commit": CURRENT_UPSTREAM_COMMIT,
            "checked_at": "2026-07-16",
        },
        "claims": claims,
    }


FIXTURE_CLAIMS = [
    _claim("multi-action-ranking", "multi-action probabilities drive ranking", "confirmed-current"),
    _claim("weights-not-public", "numeric weight values are unknown", "unknown"),
    _claim("link-penalty", "universal link penalty", "unsupported"),
    _claim("hashtags", "fixed hashtag bonus", "unsupported"),
    _claim("photo-expand", "photo expansion is predicted", "confirmed-current"),
    _claim("video-view", "video view is predicted", "confirmed-current"),
    _claim("quote-actions", "quote actions are predicted", "confirmed-current"),
    *[
        _claim(f"fixture-{index}", f"fixture claim {index}", "confirmed-current")
        for index in range(12)
    ],
]


class RegistryAndCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry_path = Path(self.temp_dir.name) / "claims.json"
        self.registry_path.write_text(json.dumps(_registry(FIXTURE_CLAIMS)), encoding="utf-8")
        self.registry = load_registry(self.registry_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_audit_refuses_fake_score_and_labels_link_claim(self) -> None:
        report = audit_draft(self.registry, "Read https://example.com #recsys", has_image=True)
        self.assertIsNone(report["score"])
        self.assertEqual(report["draft"]["links"], 1)
        self.assertEqual(report["draft"]["hashtags"], 1)
        verdicts = {item["verdict"] for item in report["observations"]}
        self.assertIn("confirmed-current", verdicts)
        self.assertIn("unsupported", verdicts)
        self.assertIn("unknown", verdicts)

    def test_validate_command(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            status = main(["--registry", str(self.registry_path), "validate"])
        self.assertEqual(status, 0)
        self.assertIn("19 claims", output.getvalue())

    def test_duplicate_claim_ids_are_rejected(self) -> None:
        duplicated = [*FIXTURE_CLAIMS[:18], FIXTURE_CLAIMS[0]]
        self.registry_path.write_text(json.dumps(_registry(duplicated)), encoding="utf-8")
        with self.assertRaisesRegex(RegistryError, "Duplicate claim id"):
            load_registry(self.registry_path)


class DriftCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location(
            "check_upstream", ROOT / "scripts" / "check_upstream.py"
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load drift checker")
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_registry_supplies_default_pin(self) -> None:
        self.assertEqual(
            self.module.pinned_commit_from_registry(ROOT / "claims" / "claims.json"),
            CURRENT_UPSTREAM_COMMIT,
        )

    def test_no_drift(self) -> None:
        def fetcher(url: str, token: str | None) -> dict[str, str]:
            return {"sha": CURRENT_UPSTREAM_COMMIT, "html_url": "https://example.test/commit"}

        result = self.module.check_drift(CURRENT_UPSTREAM_COMMIT, fetcher=fetcher)
        self.assertFalse(result.drifted)

    def test_drift(self) -> None:
        current = "a" * 40

        def fetcher(url: str, token: str | None) -> dict[str, str]:
            return {"sha": current, "html_url": "https://example.test/commit"}

        result = self.module.check_drift(CURRENT_UPSTREAM_COMMIT, fetcher=fetcher)
        self.assertTrue(result.drifted)
        self.assertEqual(result.current_commit, current)


if __name__ == "__main__":
    unittest.main()
