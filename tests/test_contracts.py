from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"
EXAMPLES = CONTRACTS / "examples"
CLAIMS = ROOT / "claims" / "claims.json"


def _read_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return payload


class AgentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request_schema = _read_json(CONTRACTS / "x-post-optimize.request.schema.json")
        cls.response_schema = _read_json(CONTRACTS / "x-post-optimize.response.schema.json")
        cls.request = _read_json(EXAMPLES / "request.json")
        cls.response = _read_json(EXAMPLES / "response.json")
        registry = _read_json(CLAIMS)
        cls.claims = {claim["id"]: claim for claim in registry["claims"]}

    def test_schemas_are_valid_draft_2020_12(self) -> None:
        Draft202012Validator.check_schema(self.request_schema)
        Draft202012Validator.check_schema(self.response_schema)

    def test_examples_validate(self) -> None:
        Draft202012Validator(self.request_schema).validate(self.request)
        Draft202012Validator(self.response_schema).validate(self.response)
        self.assertEqual(len(self.response["variants"]), self.request["variant_count"])

    def test_example_claim_ids_resolve_with_matching_verdicts(self) -> None:
        request_ids = set(self.request["claim_ids"])
        ledger = {item["claim_id"]: item["verdict"] for item in self.response["evidence_ledger"]}
        self.assertEqual(request_ids, set(ledger))
        for claim_id, verdict in ledger.items():
            self.assertIn(claim_id, self.claims)
            self.assertEqual(verdict, self.claims[claim_id]["verdict"])

        for variant in self.response["variants"]:
            for assertion in variant["assertions"]:
                for claim_id, verdict in zip(
                    assertion["claim_ids"], assertion["verdicts"], strict=True
                ):
                    self.assertIn(claim_id, self.claims)
                    self.assertEqual(verdict, self.claims[claim_id]["verdict"])


if __name__ == "__main__":
    unittest.main()
