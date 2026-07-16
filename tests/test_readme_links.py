from __future__ import annotations

import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = [
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "docs" / "agent-contract.md",
    ROOT / "docs" / "launch-kit.md",
]
MARKDOWN_LINK = re.compile(r"!?(?:\[[^]]*\])\(([^) >]+)(?:\s+[^)]*)?\)")
HTML_LINK = re.compile(r"(?:href|src)=\"([^\"]+)\"")


class LocalDocumentationLinkTests(unittest.TestCase):
    def test_relative_links_resolve(self) -> None:
        missing: list[str] = []
        for document in DOCUMENTS:
            text = document.read_text(encoding="utf-8")
            targets = [*MARKDOWN_LINK.findall(text), *HTML_LINK.findall(text)]
            for target in targets:
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                clean_target = unquote(target.split("#", 1)[0])
                if not clean_target:
                    continue
                resolved = (document.parent / clean_target).resolve()
                if not resolved.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [], "Broken relative links:\n" + "\n".join(missing))


if __name__ == "__main__":
    unittest.main()
