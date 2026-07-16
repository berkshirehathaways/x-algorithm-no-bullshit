# Agent contract: `x_post.optimize.v1`

This is the vendor-neutral interface for adapters that draft or review X posts with the repository's evidence rules.

Machine-readable definitions:

- [`contracts/x-post-optimize.request.schema.json`](../contracts/x-post-optimize.request.schema.json)
- [`contracts/x-post-optimize.response.schema.json`](../contracts/x-post-optimize.response.schema.json)
- [`contracts/examples/request.json`](../contracts/examples/request.json)
- [`contracts/examples/response.json`](../contracts/examples/response.json)

Both schemas use JSON Schema Draft 2020-12, reject unknown top-level fields, and are checked in CI against the committed examples.

## Evidence authority

`claims/claims.json` is the canonical claim registry. An adapter MUST:

1. resolve every claim ID at execution time;
2. copy its verdict exactly;
3. apply the caller's freshness policy;
4. reject missing, stale, or mismatched evidence; and
5. keep assumptions and hypotheses separate from sourced assertions.

Verdict semantics:

- `confirmed-current` may support current wording within its cited scope.
- `legacy-only` may support historical wording only.
- `inferred` must remain explicitly framed as an inference.
- `unsupported`, `unknown`, and `contradicted` cannot support affirmative algorithm claims. They may support explicit uncertainty, rejection, or contradiction wording.

## Request

A request includes:

- `operation`: `draft` or `review`;
- `brief`: audience, goal, topic, language, voice, and constraints;
- `claim_ids`: the complete evidence set the adapter may use;
- `source_draft`: required and non-empty for review, `null` for drafting;
- `freshness_policy`: review date, maximum evidence age, and current-source requirement;
- `variant_count`: at least two for drafting; and
- `extensions`: the only vendor-specific expansion point.

See the [valid request example](../contracts/examples/request.json).

## Response

A response has status `ready`, `needs-evidence`, or `rejected` and includes:

- an evidence ledger with verdict and freshness state;
- materially distinct hooks;
- variants with assertion-level claim IDs and verdicts;
- labeled assumptions;
- rejection reasons;
- a negative-feedback review;
- a launch plan with anti-spam boundaries;
- a measurement plan with causal limits; and
- explicit limitations.

A `ready` response contains publishable variants. `needs-evidence` and `rejected` responses contain no variants and at least one rejection reason. See the [valid response example](../contracts/examples/response.json).

## Safety and epistemic limits

Adapters MUST reject fabricated reach scores, unpublished weights, guarantees of virality, harassment, spam, engagement pods, deceptive bait, fabricated evidence, and legacy claims presented as current.

`action_affordances` describe relevant reader actions a post makes natural—replying with experience, saving a reference, or quoting a defensible disagreement. They MUST NOT imply a ranking bonus.

Observed launch metrics do not establish an algorithmic effect. The public source does not expose the live personalized weights, viewer context, production checkpoint, candidate set, or experiments needed for a deterministic score.

## Conformance

```bash
python -m pip install -e ".[dev]"
python -m unittest tests.test_contracts -v
```

Adapters may add data only inside `extensions`; changing required field meanings requires a new schema version.
