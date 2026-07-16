from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SourceVerifierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location(
            "verify_sources", ROOT / "scripts" / "verify_sources.py"
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load source verifier")
        cls.module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.module
        spec.loader.exec_module(cls.module)

    def test_registry_sources_become_pinned_raw_urls(self) -> None:
        checks = self.module.checks_from_registry(ROOT / "claims" / "claims.json")
        self.assertGreaterEqual(len(checks), 19)
        for check in checks:
            self.assertIn("raw.githubusercontent.com", check.raw_url)
            if "xai-org/x-algorithm" in check.raw_url:
                self.assertIn("/0bfc2795d308f90032544322747caacd535f75ae/", check.raw_url)

    def test_existing_nonempty_range_passes(self) -> None:
        check = self.module.SourceCheck(
            url="https://example.test/source#L2-L3",
            raw_url="https://example.test/source",
            line_start=2,
            line_end=3,
        )
        self.assertIsNone(self.module.verify_source(check, fetcher=lambda _: "one\ntwo\nthree\n"))

    def test_out_of_bounds_range_fails(self) -> None:
        check = self.module.SourceCheck(
            url="https://example.test/source#L2-L4",
            raw_url="https://example.test/source",
            line_start=2,
            line_end=4,
        )
        error = self.module.verify_source(check, fetcher=lambda _: "one\ntwo\n")
        self.assertIn("source has 2 lines", error)


if __name__ == "__main__":
    unittest.main()
