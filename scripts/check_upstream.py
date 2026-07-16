#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPOSITORY = "xai-org/x-algorithm"
DEFAULT_BRANCH = "main"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "claims" / "claims.json"
API_URL = f"https://api.github.com/repos/{REPOSITORY}/commits/{DEFAULT_BRANCH}"


@dataclass(frozen=True)
class DriftResult:
    repository: str
    branch: str
    pinned_commit: str
    current_commit: str
    drifted: bool
    commit_url: str


def fetch_json(url: str, token: str | None = None) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "x-algorithm-no-bullshit-drift-checker",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("GitHub returned a non-object response")
    return payload


def pinned_commit_from_registry(path: Path = DEFAULT_REGISTRY) -> str:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    upstream = payload.get("upstream") if isinstance(payload, dict) else None
    commit = upstream.get("commit") if isinstance(upstream, dict) else None
    if not isinstance(commit, str):
        raise ValueError("Registry does not contain upstream.commit")
    return commit


def check_drift(
    pinned_commit: str,
    *,
    fetcher: Callable[[str, str | None], dict[str, Any]] = fetch_json,
    token: str | None = None,
) -> DriftResult:
    payload = fetcher(API_URL, token)
    current = payload.get("sha")
    if not isinstance(current, str) or len(current) != 40:
        raise ValueError("GitHub response does not contain a full commit SHA")
    html_url = payload.get("html_url")
    if not isinstance(html_url, str):
        html_url = f"https://github.com/{REPOSITORY}/commit/{current}"
    return DriftResult(
        repository=REPOSITORY,
        branch=DEFAULT_BRANCH,
        pinned_commit=pinned_commit,
        current_commit=current,
        drifted=current != pinned_commit,
        commit_url=html_url,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fail when the public X algorithm moves past this evidence registry's pin."
    )
    parser.add_argument("--pin", help="Override the evidence registry's upstream commit")
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="Claims registry supplying the default upstream pin",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--github-output",
        type=Path,
        help="Append drift fields to a GitHub Actions output file",
    )
    return parser


def _write_github_output(path: Path, result: DriftResult) -> None:
    with path.open("a", encoding="utf-8") as output:
        output.write(f"drifted={'true' if result.drifted else 'false'}\n")
        output.write(f"pinned_commit={result.pinned_commit}\n")
        output.write(f"current_commit={result.current_commit}\n")
        output.write(f"commit_url={result.commit_url}\n")


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        pin = args.pin or pinned_commit_from_registry(args.registry)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"check_upstream: cannot read evidence pin: {exc}", file=sys.stderr)
        return 2
    if len(pin) != 40 or any(ch not in "0123456789abcdef" for ch in pin.lower()):
        print("check_upstream: pin must be a full 40-character hexadecimal SHA", file=sys.stderr)
        return 2
    try:
        result = check_drift(pin.lower(), token=os.environ.get("GITHUB_TOKEN"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        print(f"check_upstream: could not query GitHub: {exc}", file=sys.stderr)
        return 4

    if args.github_output:
        _write_github_output(args.github_output, result)
    if args.json:
        print(json.dumps(asdict(result), indent=2))
    elif result.drifted:
        print(
            "DRIFT: upstream changed\n"
            f"  pinned:  {result.pinned_commit}\n"
            f"  current: {result.current_commit}\n"
            f"  review:  {result.commit_url}"
        )
    else:
        print(f"OK: evidence registry is pinned to current upstream {result.current_commit}")
    return 3 if result.drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())
