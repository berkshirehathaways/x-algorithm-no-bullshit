# Contributing

Corrections beat more content. Contributions should make a claim easier to verify, not merely more confident.

## Correct or add a claim

1. Pin a primary-source repository and full commit SHA.
2. Cite the smallest useful line range.
3. Choose exactly one verdict: `confirmed-current`, `legacy-only`, `inferred`, `unsupported`, `unknown`, or `contradicted`.
4. Keep the claim atomic. Separate a current fact from an unknown value or historical comparison.
5. State the practical implication without promising reach or virality.
6. Update `claims/claims.json` and regenerate derived files:

```bash
python scripts/generate_cards.py
```

## Verify

```bash
python -m pip install -e ".[dev]"
xnb validate
ruff check src scripts tests
ruff format --check src scripts tests
python scripts/generate_cards.py --check
python -m unittest discover -s tests -v
python scripts/verify_sources.py
```

`verify_sources.py` uses the network to resolve pinned citations. The remaining gates are deterministic and offline.

## Pull requests

Explain which claim IDs changed and why their verdicts remain valid or need revision. Do not mix unrelated copy, tooling, and evidence changes. Claims derived from private dashboards, anonymous screenshots, or uncited growth folklore will not be accepted as current evidence.

This project is independent and unaffiliated with X, xAI, or Twitter. Follow the upstream licenses when quoting source; prefer links and short excerpts over copied code.
