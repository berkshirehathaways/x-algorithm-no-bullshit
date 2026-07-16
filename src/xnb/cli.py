from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from xnb.registry import ALLOWED_VERDICTS, Registry, RegistryError, load_registry

URL_PATTERN = re.compile(
    r"https?://\S+|(?:^|\s)(?:www\.)?[^\s.]+\.[a-z]{2,}(?:/\S*)?", re.IGNORECASE
)
HASHTAG_PATTERN = re.compile(r"(?<!\w)#[\w-]+", re.UNICODE)


def _claim_ref(registry: Registry, query: str, verdict: str | None = None) -> str | None:
    verdicts = [verdict] if verdict else None
    matches = registry.search(query, verdicts)
    return matches[0]["id"] if matches else None


def _preferred_claim_ref(registry: Registry, claim_id: str, fallback_query: str) -> str | None:
    try:
        return registry.by_id(claim_id)["id"]
    except RegistryError:
        return _claim_ref(registry, fallback_query)


def audit_draft(
    registry: Registry,
    text: str,
    *,
    has_image: bool = False,
    has_video: bool = False,
    is_quote: bool = False,
) -> dict[str, Any]:
    links = URL_PATTERN.findall(text)
    hashtags = HASHTAG_PATTERN.findall(text)
    observations: list[dict[str, Any]] = []

    observations.append(
        {
            "verdict": "confirmed-current",
            "finding": (
                "X's public ranker predicts multiple positive and negative viewer actions; "
                "a draft alone does not reveal those probabilities."
            ),
            "claim_id": _claim_ref(registry, "multi-action", "confirmed-current"),
        }
    )
    observations.append(
        {
            "verdict": "unknown",
            "finding": (
                "No numeric virality score is produced because current live weights, viewer "
                "context, production checkpoints, and experiments are unavailable."
            ),
            "claim_id": _preferred_claim_ref(
                registry, "current-numeric-ranking-weights", "numeric weight"
            ),
        }
    )

    if links:
        observations.append(
            {
                "verdict": "unsupported",
                "finding": (
                    "A universal 2026 outbound-link penalty is not established by the current "
                    "public source. Click probability is modeled, but net effect remains "
                    "context-dependent."
                ),
                "claim_id": _claim_ref(registry, "link", "unsupported"),
            }
        )
    if hashtags:
        observations.append(
            {
                "verdict": "unknown",
                "finding": (
                    "The local evidence registry contains no confirmed current claim for a "
                    "fixed hashtag bonus or penalty. Treat hashtag advice as a testable "
                    "hypothesis."
                ),
                "claim_id": _claim_ref(registry, "hashtag"),
                "count": len(hashtags),
            }
        )
    if has_image:
        observations.append(
            {
                "verdict": "confirmed-current",
                "finding": (
                    "Photo expansion is a predicted action. Attaching an image creates the "
                    "affordance; it does not guarantee a ranking bonus."
                ),
                "claim_id": _preferred_claim_ref(
                    registry, "current-ranker-22-score-terms", "multi-action"
                ),
            }
        )
    if has_video:
        observations.append(
            {
                "verdict": "confirmed-current",
                "finding": (
                    "Video quality view is a conditional predicted action. The production "
                    "duration threshold and live weight are runtime parameters."
                ),
                "claim_id": _preferred_claim_ref(
                    registry, "current-ranker-22-score-terms", "multi-action"
                ),
            }
        )
    if is_quote:
        observations.append(
            {
                "verdict": "confirmed-current",
                "finding": (
                    "Quote, quoted-click, and quoted-video-view are modeled actions. Whether "
                    "this draft earns them is model- and audience-dependent."
                ),
                "claim_id": _preferred_claim_ref(
                    registry, "current-ranker-22-score-terms", "multi-action"
                ),
            }
        )

    return {
        "score": None,
        "score_reason": "Public source cannot reproduce the live personalized ranker.",
        "draft": {
            "characters": len(text),
            "links": len(links),
            "hashtags": len(hashtags),
            "has_image": has_image,
            "has_video": has_video,
            "is_quote": is_quote,
        },
        "observations": observations,
        "experiment": {
            "recommendation": (
                "Publish materially different variants across comparable audience/time windows "
                "and measure impressions, dwell proxies, replies, shares, negative feedback, "
                "and follows."
            ),
            "warning": (
                "Do not infer causality from one post or optimize for engagement bait that "
                "increases hides, mutes, blocks, or reports."
            ),
        },
    }


def _print_claim(claim: dict[str, Any]) -> None:
    print(f"[{claim['verdict']}] {claim['id']}")
    print(f"  {claim['claim']}")
    print(f"  Implication: {claim['practical_implication']}")
    if claim["sources"]:
        print(f"  Source: {claim['sources'][0]['url']}")


def _read_text(value: str) -> str:
    if value == "-":
        return sys.stdin.read().strip()
    try:
        candidate = Path(value)
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8").strip()
    except OSError:
        pass
    return value.strip()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="xnb",
        description="Audit X algorithm claims without inventing the missing knobs.",
    )
    parser.add_argument("--registry", help="Path to claims.json")
    subparsers = parser.add_subparsers(dest="command", required=True)

    claims_parser = subparsers.add_parser("claims", help="List or search evidence claims")
    claims_parser.add_argument("query", nargs="?", default="")
    claims_parser.add_argument(
        "--verdict",
        action="append",
        choices=sorted(ALLOWED_VERDICTS),
        help="Filter by verdict; repeat for multiple verdicts",
    )
    claims_parser.add_argument("--json", action="store_true", help="Emit JSON")

    show_parser = subparsers.add_parser("show", help="Show one claim by id")
    show_parser.add_argument("claim_id")
    show_parser.add_argument("--json", action="store_true", help="Emit JSON")

    audit_parser = subparsers.add_parser(
        "audit", help="Audit a post draft's evidence boundaries; never emits a fake score"
    )
    audit_parser.add_argument("text", help="Draft text, a text-file path, or - for stdin")
    audit_parser.add_argument("--has-image", action="store_true")
    audit_parser.add_argument("--has-video", action="store_true")
    audit_parser.add_argument("--is-quote", action="store_true")
    audit_parser.add_argument("--json", action="store_true", help="Emit JSON")

    subparsers.add_parser("validate", help="Validate the claims registry")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        registry = load_registry(args.registry)
        if args.command == "claims":
            matches = registry.search(args.query, args.verdict)
            if args.json:
                print(json.dumps(matches, indent=2, ensure_ascii=False))
            else:
                for claim in matches:
                    _print_claim(claim)
                print(f"\n{len(matches)} claim(s)")
            return 0
        if args.command == "show":
            claim = registry.by_id(args.claim_id)
            if args.json:
                print(json.dumps(claim, indent=2, ensure_ascii=False))
            else:
                _print_claim(claim)
                print(f"  Evidence: {claim['evidence_summary']}")
            return 0
        if args.command == "audit":
            text = _read_text(args.text)
            if not text:
                parser.error("audit text cannot be empty")
            report = audit_draft(
                registry,
                text,
                has_image=args.has_image,
                has_video=args.has_video,
                is_quote=args.is_quote,
            )
            if args.json:
                print(json.dumps(report, indent=2, ensure_ascii=False))
            else:
                print("NO VIRALITY SCORE — the public source does not expose the live knobs.\n")
                for item in report["observations"]:
                    claim_ref = f" ({item['claim_id']})" if item.get("claim_id") else ""
                    print(f"[{item['verdict']}]{claim_ref} {item['finding']}")
                print(f"\nExperiment: {report['experiment']['recommendation']}")
            return 0
        if args.command == "validate":
            print(f"OK: {len(registry.claims)} claims in {registry.path}")
            return 0
    except RegistryError as exc:
        print(f"xnb: {exc}", file=sys.stderr)
        return 2
    return 1
