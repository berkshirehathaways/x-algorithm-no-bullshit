#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "claims" / "claims.json"


@dataclass(frozen=True)
class SourceCheck:
    url: str
    raw_url: str
    line_start: int
    line_end: int


def raw_url_for(source: dict[str, object]) -> str:
    repository = str(source["repository"])
    commit = str(source["commit"])
    path = quote(str(source["path"]), safe="/")
    return f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"


def checks_from_registry(path: Path) -> list[SourceCheck]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    claims = payload.get("claims")
    if not isinstance(claims, list):
        raise ValueError("Registry does not contain a claims array")

    checks: dict[tuple[str, int, int], SourceCheck] = {}
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("sources"), list):
            raise ValueError("Registry contains a malformed claim")
        for source in claim["sources"]:
            if not isinstance(source, dict):
                raise ValueError("Registry contains a malformed source")
            start = source.get("line_start")
            end = source.get("line_end")
            url = source.get("url")
            if not isinstance(start, int) or not isinstance(end, int) or not isinstance(url, str):
                raise ValueError("Registry source has invalid URL or line range")
            check = SourceCheck(
                url=url,
                raw_url=raw_url_for(source),
                line_start=start,
                line_end=end,
            )
            checks[(check.raw_url, start, end)] = check
    return sorted(checks.values(), key=lambda item: (item.raw_url, item.line_start, item.line_end))


def fetch_text(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "x-algorithm-no-bullshit-source-verifier"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def verify_source(
    check: SourceCheck,
    *,
    fetcher: Callable[[str], str] = fetch_text,
) -> str | None:
    text = fetcher(check.raw_url)
    lines = text.splitlines()
    if check.line_end > len(lines):
        return f"range ends at L{check.line_end}, but source has {len(lines)} lines"
    excerpt = lines[check.line_start - 1 : check.line_end]
    if not any(line.strip() for line in excerpt):
        return "cited line range is empty"
    return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve every pinned citation and verify that its line range exists."
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--workers", type=int, default=6)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.workers < 1:
        print("verify_sources: --workers must be positive", file=sys.stderr)
        return 2
    try:
        checks = checks_from_registry(args.registry)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"verify_sources: {exc}", file=sys.stderr)
        return 2

    failures: list[tuple[SourceCheck, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(verify_source, check): check for check in checks}
        for future in as_completed(futures):
            check = futures[future]
            try:
                error = future.result()
            except (urllib.error.URLError, UnicodeDecodeError, TimeoutError, OSError) as exc:
                error = f"fetch failed: {exc}"
            if error:
                failures.append((check, error))

    if failures:
        for check, error in sorted(failures, key=lambda item: item[0].url):
            print(f"FAIL {check.url}: {error}", file=sys.stderr)
        return 1
    print(f"OK: resolved {len(checks)} unique pinned source ranges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
