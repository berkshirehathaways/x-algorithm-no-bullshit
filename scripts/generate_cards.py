#!/usr/bin/env python3
"""Generate deterministic, evidence-linked claim cards and claim index."""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "claims" / "claims.json"
OUTPUTS = {
    "weights-runtime.svg": ROOT / "assets" / "cards" / "weights-runtime.svg",
    "reply-75-legacy.svg": ROOT / "assets" / "cards" / "reply-75-legacy.svg",
    "score-terms.svg": ROOT / "assets" / "cards" / "score-terms.svg",
    "README.md": ROOT / "claims" / "README.md",
}
VERDICTS = (
    "confirmed-current",
    "legacy-only",
    "inferred",
    "unsupported",
    "unknown",
    "contradicted",
)
CARDS = (
    {
        "output": "weights-runtime.svg",
        "id": "current-numeric-ranking-weights",
        "verdict": "unknown",
        "accent": "#B680FF",
        "eyebrow": "BOUNDED PUBLIC SOURCE",
        "headline": ("LIVE NUMERIC WEIGHTS", "NOT ESTABLISHED"),
        "support": (
            "Public code reads score-term weights from runtime Params.",
            "The bounded snapshot does not establish their live values.",
        ),
    },
    {
        "output": "reply-75-legacy.svg",
        "id": "reply-75-or-150x",
        "verdict": "legacy-only",
        "accent": "#FFB000",
        "eyebrow": "HISTORICAL CONTEXT",
        "headline": ("+75 / 150×", "IS LEGACY CONTEXT"),
        "support": (
            "75.0 versus 0.5 was published for April 5, 2023.",
            "The derived 150× ratio is historical—not a current boost.",
        ),
    },
    {
        "output": "score-terms.svg",
        "id": "current-ranker-22-score-terms",
        "verdict": "confirmed-current",
        "accent": "#7C9CFF",
        "eyebrow": "CURRENT RANKINGSCORER",
        "headline": ("22 SCORE TERMS", "NOT ONE METRIC"),
        "support": (
            "The scorer combines 22 named Phoenix score terms.",
            "That is not evidence of published runtime weights.",
        ),
    },
)


def svg_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def markdown_text(value: object) -> str:
    """Escape registry text used as Markdown prose."""
    text = str(value).replace("\\", "\\\\")
    for character in "`*_{}[]<>#|":
        text = text.replace(character, f"\\{character}")
    return text.replace("\n", " ")


def markdown_code(value: object) -> str:
    return str(value).replace("`", "\\`").replace("\\", "\\\\")


def source_label(source: dict[str, object]) -> str:
    return "{repository} @ {commit} — {path}:L{start}-L{end}".format(
        repository=source["repository"],
        commit=str(source["commit"])[:8],
        path=source["path"],
        start=source["line_start"],
        end=source["line_end"],
    )


def source_link(source: dict[str, object]) -> str:
    # An HTML-escaped autolink preserves a source URL without Markdown delimiter injection.
    return (
        f"[{markdown_text(source_label(source))}](<{html.escape(str(source['url']), quote=True)}>)"
    )


def load_claims() -> dict[str, dict[str, object]]:
    try:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read claim registry: {error}") from error
    claims = payload.get("claims")
    if not isinstance(claims, list):
        raise ValueError("Claim registry must contain a claims list")

    by_id: dict[str, dict[str, object]] = {}
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("id"), str):
            raise ValueError("Every claim must be an object with a string id")
        claim_id = claim["id"]
        if claim_id in by_id:
            raise ValueError(f"Duplicate claim id: {claim_id}")
        validate_claim(claim)
        by_id[claim_id] = claim
    return by_id


def validate_claim(claim: dict[str, object]) -> None:
    claim_id = claim["id"]
    for field in (
        "claim",
        "verdict",
        "practical_implication",
        "evidence_summary",
        "upstream_commit",
        "sources",
    ):
        if not claim.get(field):
            raise ValueError(f"Claim {claim_id} is missing {field}")
    if claim["verdict"] not in VERDICTS:
        raise ValueError(f"Claim {claim_id} has invalid verdict: {claim['verdict']}")
    if not isinstance(claim["sources"], list):
        raise ValueError(f"Claim {claim_id} sources must be a list")
    for source in claim["sources"]:
        if not isinstance(source, dict):
            raise ValueError(f"Claim {claim_id} has an invalid source")
        required = ("repository", "commit", "path", "line_start", "line_end", "url")
        if any(not source.get(field) for field in required):
            raise ValueError(f"Claim {claim_id} has a missing source field")
        parsed = urlparse(str(source["url"]))
        if parsed.scheme != "https" or not parsed.netloc or not parsed.fragment:
            raise ValueError(f"Claim {claim_id} has an invalid anchored source URL")


def render_card(spec: dict[str, object], claim: dict[str, object]) -> str:
    source = claim["sources"][0]
    assert isinstance(source, dict)
    headline = spec["headline"]
    support = spec["support"]
    assert isinstance(headline, tuple) and isinstance(support, tuple)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-labelledby="title description">
  <title id="title">{svg_text(headline[0])}</title>
  <desc id="description">Claim {svg_text(claim["id"])}: {svg_text(claim["claim"])}</desc>
  <rect width="1200" height="630" fill="#090B10"/>
  <rect x="48" y="48" width="8" height="534" fill="{svg_text(spec["accent"])}"/>
  <text x="88" y="103" fill="{svg_text(spec["accent"])}" font-family="Arial, Helvetica, sans-serif" font-size="22" font-weight="700" letter-spacing="3">{svg_text(spec["eyebrow"])}</text>
  <text x="88" y="214" fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif" font-size="73" font-weight="700">{svg_text(headline[0])}</text>
  <text x="88" y="299" fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif" font-size="73" font-weight="700">{svg_text(headline[1])}</text>
  <line x1="88" y1="345" x2="1112" y2="345" stroke="#3A4150" stroke-width="2"/>
  <text x="88" y="397" fill="#DCE2EF" font-family="Arial, Helvetica, sans-serif" font-size="27">{svg_text(support[0])}</text>
  <text x="88" y="435" fill="#DCE2EF" font-family="Arial, Helvetica, sans-serif" font-size="27">{svg_text(support[1])}</text>
  <text x="88" y="501" fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700">CLAIM ID  {svg_text(claim["id"])}</text>
  <text x="88" y="535" fill="#FFFFFF" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="700">VERDICT  {svg_text(claim["verdict"])}    PIN  {svg_text(str(claim["upstream_commit"])[:8])}</text>
  <text x="88" y="569" fill="#AEB8CC" font-family="Arial, Helvetica, sans-serif" font-size="16">SOURCE  {svg_text(source["path"])}:L{svg_text(source["line_start"])}-L{svg_text(source["line_end"])}</text>
</svg>
'''


def render_index(claims: dict[str, dict[str, object]]) -> str:
    lines = [
        "# Claim index",
        "",
        "Generated from `claims/claims.json`; do not edit by hand.",
        "",
        "Regenerate: `python3 scripts/generate_cards.py`",
        "",
    ]
    for verdict in VERDICTS:
        grouped = [claim for claim in claims.values() if claim["verdict"] == verdict]
        if not grouped:
            continue
        lines.extend((f"## {verdict}", ""))
        for claim in grouped:
            lines.extend(
                (
                    f"### `{markdown_code(claim['id'])}`",
                    "",
                    f"**Claim:** {markdown_text(claim['claim'])}",
                    "",
                    f"**Practical implication:** {markdown_text(claim['practical_implication'])}",
                    "",
                    f"**Evidence:** {markdown_text(claim['evidence_summary'])}",
                    "",
                    "**Sources:**",
                )
            )
            for source in claim["sources"]:
                assert isinstance(source, dict)
                lines.append(f"- {source_link(source)}")
            lines.append("")
    return "\n".join(lines)


def generated_files() -> dict[Path, str]:
    claims = load_claims()
    rendered: dict[Path, str] = {}
    for spec in CARDS:
        claim = claims.get(str(spec["id"]))
        if claim is None:
            raise ValueError(f"Required card claim is missing: {spec['id']}")
        if claim["verdict"] != spec["verdict"]:
            raise ValueError(f"Required claim {spec['id']} must retain verdict {spec['verdict']}")
        rendered[OUTPUTS[str(spec["output"])]] = render_card(spec, claim)
    rendered[OUTPUTS["README.md"]] = render_index(claims)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail unless committed outputs are current"
    )
    args = parser.parse_args()
    try:
        outputs = generated_files()
    except ValueError as error:
        print(f"generate_cards.py: {error}", file=sys.stderr)
        return 1

    stale = []
    for path, content in outputs.items():
        encoded = content.encode("utf-8")
        if args.check:
            if not path.is_file() or path.read_bytes() != encoded:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
    if stale:
        print("Generated files are stale: " + ", ".join(map(str, stale)), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
