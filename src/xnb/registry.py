from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CURRENT_UPSTREAM_COMMIT = "0bfc2795d308f90032544322747caacd535f75ae"
ALLOWED_VERDICTS = {
    "confirmed-current",
    "legacy-only",
    "inferred",
    "unsupported",
    "unknown",
    "contradicted",
}
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_URL_PATTERN = re.compile(
    r"^https://github\.com/(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/blob/"
    r"(?P<commit>[0-9a-f]{40})/(?P<path>.+)#L(?P<start>[1-9][0-9]*)-L(?P<end>[1-9][0-9]*)$"
)


class RegistryError(ValueError):
    """Raised when the evidence registry is absent or malformed."""


@dataclass(frozen=True)
class Registry:
    path: Path
    claims: tuple[dict[str, Any], ...]
    metadata: dict[str, Any]

    def by_id(self, claim_id: str) -> dict[str, Any]:
        for claim in self.claims:
            if claim["id"] == claim_id:
                return claim
        raise RegistryError(f"Unknown claim id: {claim_id}")

    def search(
        self, query: str = "", verdicts: Iterable[str] | None = None
    ) -> list[dict[str, Any]]:
        wanted = set(verdicts or ())
        needle = query.casefold().strip()
        matches: list[dict[str, Any]] = []
        for claim in self.claims:
            if wanted and claim["verdict"] not in wanted:
                continue
            haystack = " ".join(
                str(claim.get(key, ""))
                for key in ("id", "claim", "evidence_summary", "practical_implication")
            ).casefold()
            if not needle or needle in haystack:
                matches.append(claim)
        return matches


def _registry_candidates(explicit: str | Path | None) -> list[Path]:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    if configured := os.environ.get("XNB_CLAIMS"):
        candidates.append(Path(configured).expanduser())
    candidates.extend(
        [
            Path.cwd() / "claims" / "claims.json",
            Path(__file__).resolve().parents[2] / "claims" / "claims.json",
            Path(sys.prefix) / "share" / "xnb" / "claims.json",
        ]
    )
    return candidates


def find_registry_path(explicit: str | Path | None = None) -> Path:
    for candidate in _registry_candidates(explicit):
        if candidate.is_file():
            return candidate.resolve()
    checked = ", ".join(str(path) for path in _registry_candidates(explicit))
    raise RegistryError(f"Could not find claims registry. Checked: {checked}")


def _extract_claims(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, dict) or not isinstance(raw.get("claims"), list):
        raise RegistryError("Registry must be an object containing a claims array")
    claims = raw["claims"]
    if not all(isinstance(item, dict) for item in claims):
        raise RegistryError("Every claim must be a JSON object")
    return claims


def validate_metadata(raw: dict[str, Any]) -> None:
    required = {"schema_version", "registry_version", "reviewed_at", "upstream", "claims"}
    if set(raw) != required:
        raise RegistryError(
            f"Registry top-level fields must be exactly: {', '.join(sorted(required))}"
        )
    if raw["schema_version"] != "1.0.0":
        raise RegistryError("Unsupported registry schema_version")
    if not isinstance(raw["registry_version"], str) or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+", raw["registry_version"]
    ):
        raise RegistryError("registry_version must use semantic version syntax")
    if not isinstance(raw["reviewed_at"], str) or not DATE_PATTERN.fullmatch(raw["reviewed_at"]):
        raise RegistryError("reviewed_at must be an ISO calendar date")
    upstream = raw["upstream"]
    expected_upstream = {"repository", "commit", "checked_at"}
    if not isinstance(upstream, dict) or set(upstream) != expected_upstream:
        raise RegistryError("upstream metadata is malformed")
    if upstream["repository"] != "xai-org/x-algorithm":
        raise RegistryError("upstream repository must be xai-org/x-algorithm")
    if upstream["commit"] != CURRENT_UPSTREAM_COMMIT:
        raise RegistryError("upstream commit does not match the supported evidence pin")
    if not isinstance(upstream["checked_at"], str) or not DATE_PATTERN.fullmatch(
        upstream["checked_at"]
    ):
        raise RegistryError("upstream.checked_at must be an ISO calendar date")


def validate_claims(claims: list[dict[str, Any]]) -> None:
    required = {
        "id",
        "claim",
        "verdict",
        "practical_implication",
        "evidence_summary",
        "upstream_commit",
        "sources",
    }
    seen: set[str] = set()
    if len(claims) < 19:
        raise RegistryError("Registry must contain at least 19 claims")
    for index, claim in enumerate(claims):
        if set(claim) != required:
            raise RegistryError(
                f"Claim #{index} fields must be exactly: {', '.join(sorted(required))}"
            )
        claim_id = claim["id"]
        if not isinstance(claim_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", claim_id):
            raise RegistryError(f"Claim #{index} has an invalid id")
        if claim_id in seen:
            raise RegistryError(f"Duplicate claim id: {claim_id}")
        seen.add(claim_id)
        verdict = claim["verdict"]
        if verdict not in ALLOWED_VERDICTS:
            raise RegistryError(f"{claim_id} has invalid verdict: {verdict}")
        for key in ("claim", "practical_implication", "evidence_summary"):
            if not isinstance(claim[key], str) or not claim[key].strip():
                raise RegistryError(f"{claim_id} has an invalid {key}")
        if not isinstance(claim["upstream_commit"], str) or not SHA_PATTERN.fullmatch(
            claim["upstream_commit"]
        ):
            raise RegistryError(f"{claim_id} has an invalid upstream_commit")
        sources = claim["sources"]
        if not isinstance(sources, list) or not sources:
            raise RegistryError(f"{claim_id} sources must be a non-empty array")
        for source in sources:
            required_source = {
                "repository",
                "commit",
                "path",
                "line_start",
                "line_end",
                "url",
            }
            if not isinstance(source, dict) or set(source) != required_source:
                raise RegistryError(f"{claim_id} contains a malformed source")
            start, end = source["line_start"], source["line_end"]
            if not isinstance(start, int) or not isinstance(end, int) or start < 1 or end < start:
                raise RegistryError(f"{claim_id} has an invalid source line range")
            match = SOURCE_URL_PATTERN.fullmatch(source["url"])
            if not match:
                raise RegistryError(f"{claim_id} has an invalid pinned source URL")
            if (
                match["repository"] != source["repository"]
                or match["commit"] != source["commit"]
                or match["path"] != source["path"]
                or int(match["start"]) != start
                or int(match["end"]) != end
            ):
                raise RegistryError(f"{claim_id} source URL does not match its fields")
            if source["repository"] == "xai-org/x-algorithm":
                if source["commit"] != CURRENT_UPSTREAM_COMMIT:
                    raise RegistryError(f"{claim_id} does not pin the current upstream")
                if claim["upstream_commit"] != CURRENT_UPSTREAM_COMMIT:
                    raise RegistryError(f"{claim_id} upstream_commit disagrees with its source")


def load_registry(path: str | Path | None = None) -> Registry:
    registry_path = find_registry_path(path)
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"Cannot read registry at {registry_path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise RegistryError("Registry root must be a JSON object")
    validate_metadata(raw)
    claims = _extract_claims(raw)
    validate_claims(claims)
    metadata = {key: value for key, value in raw.items() if key != "claims"}
    return Registry(path=registry_path, claims=tuple(claims), metadata=metadata)
