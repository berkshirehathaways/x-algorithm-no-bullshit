"""Offline structural checks for the X Algorithm claim registry."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "claims" / "claims.json"
CURRENT_REPOSITORY = "xai-org/x-algorithm"
CURRENT_COMMIT = "0bfc2795d308f90032544322747caacd535f75ae"
VERDICTS = {
    "confirmed-current",
    "legacy-only",
    "inferred",
    "unsupported",
    "unknown",
    "contradicted",
}
REQUIRED_CLAIM_FIELDS = {
    "id",
    "claim",
    "verdict",
    "practical_implication",
    "evidence_summary",
    "upstream_commit",
    "sources",
}
REQUIRED_SOURCE_FIELDS = {"repository", "commit", "path", "line_start", "line_end", "url"}
SHA = re.compile(r"^[0-9a-f]{40}$")
PINNED_GITHUB_URL = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/"
    r"([0-9a-f]{40})/(.+)#L([1-9][0-9]*)-L([1-9][0-9]*)$"
)


class ClaimRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRY.open(encoding="utf-8") as registry_file:
            cls.registry = json.load(registry_file)
            cls.claims = cls.registry["claims"]

    def test_registry_metadata_is_pinned_and_versioned(self):
        self.assertEqual(self.registry["schema_version"], "1.0.0")
        self.assertRegex(self.registry["registry_version"], r"^[0-9]+\.[0-9]+\.[0-9]+$")
        self.assertEqual(self.registry["reviewed_at"], "2026-07-16")
        self.assertEqual(self.registry["upstream"]["repository"], CURRENT_REPOSITORY)
        self.assertEqual(self.registry["upstream"]["commit"], CURRENT_COMMIT)
        self.assertEqual(self.registry["upstream"]["checked_at"], "2026-07-16")

    def test_registry_has_unique_ids_and_required_fields(self):
        self.assertGreaterEqual(len(self.claims), 19)
        ids = []
        for claim in self.claims:
            self.assertEqual(set(claim), REQUIRED_CLAIM_FIELDS)
            self.assertTrue(all(claim[field] for field in REQUIRED_CLAIM_FIELDS - {"sources"}))
            self.assertIsInstance(claim["sources"], list)
            self.assertTrue(claim["sources"])
            ids.append(claim["id"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_verdicts_and_commits_are_valid(self):
        for claim in self.claims:
            self.assertIn(claim["verdict"], VERDICTS)
            self.assertRegex(claim["upstream_commit"], SHA)

    def test_sources_have_valid_pinned_github_locations(self):
        for claim in self.claims:
            for source in claim["sources"]:
                self.assertEqual(set(source), REQUIRED_SOURCE_FIELDS)
                self.assertRegex(source["commit"], SHA)
                self.assertTrue(source["path"])
                self.assertIsInstance(source["line_start"], int)
                self.assertIsInstance(source["line_end"], int)
                self.assertGreaterEqual(source["line_start"], 1)
                self.assertGreaterEqual(source["line_end"], source["line_start"])
                match = PINNED_GITHUB_URL.fullmatch(source["url"])
                self.assertIsNotNone(match)
                self.assertEqual(match.group(1), source["repository"])
                self.assertEqual(match.group(2), source["commit"])
                self.assertEqual(match.group(3), source["path"])
                self.assertEqual(int(match.group(4)), source["line_start"])
                self.assertEqual(int(match.group(5)), source["line_end"])

    def test_current_claims_pin_the_current_upstream_commit(self):
        for claim in self.claims:
            current_source = any(
                source["repository"] == CURRENT_REPOSITORY for source in claim["sources"]
            )
            if claim["verdict"] == "confirmed-current" or current_source:
                self.assertEqual(claim["upstream_commit"], CURRENT_COMMIT)
            for source in claim["sources"]:
                if source["repository"] == CURRENT_REPOSITORY:
                    self.assertEqual(source["commit"], CURRENT_COMMIT)


if __name__ == "__main__":
    unittest.main()
