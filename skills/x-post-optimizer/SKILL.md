---
name: x-post-optimizer
description: Create evidence-first X post variants and launch plans without fabricating algorithmic certainty or virality.
metadata:
  product: X Algorithm: No Bullshit
  cli: xnb
  language: en-first-with-ko-support
---

# X Post Optimizer

Write posts people want to share because the claim is sharp **and** the evidence is inspectable. This skill optimizes the clarity of a post's likely action affordances—replying with experience, quoting with a counterpoint, saving a useful reference, or sharing a defensible insight. It does not claim that any action earns an algorithmic bonus.

## Non-negotiable evidence contract

Before writing, read `claims/claims.json`. Every factual assertion needs a claim ID and must retain the registry verdict verbatim:

- `confirmed-current`: may be described as current, within the claim's scope and date.
- `legacy-only`: historical context only; never describe as current X behavior.
- `inferred`: frame as an inference, not an observed fact.
- `unsupported`, `unknown`, or `contradicted`: do not use as affirmative evidence.

If a requested assertion has no resolvable, fresh claim record, fail closed: omit it, ask for a sourced claim, or say what is unknown. Do not use remembered source code, old Twitter documentation, rumors, or a plausible guess to complete the post.

Never fabricate reach scores, weights, citations, engagement bonuses, or results. Do not assert that a post will go viral. Public source cannot deterministically score content because live weights, viewer and author context, production models, and experiments are unavailable.

Reject or redirect requests for harassment, spam, engagement pods, deceptive bait, impersonation, or manipulation. Do not disguise a question as a fact or manufacture conflict to trigger replies.

## Workflow

1. **Brief the job.** Record the target audience, desired outcome, language, voice, topic, evidence boundary, and constraints. Default to English; for Korean output, preserve claim IDs, verdicts, and uncertainty.
2. **Build an evidence ledger.** Resolve each proposed fact to claim IDs. Keep facts, inferences, and hypotheses separate. Note source freshness and scope. A missing or stale record is a stop, not a drafting prompt.
3. **Find the tension.** State the useful disagreement, misconception, trade-off, or surprising constraint without overstating evidence.
4. **Draft at least three distinct hooks.** Use materially different angles, such as a contrarian correction, a practical consequence, a question grounded in evidence, or a concise myth-versus-fact. Do not produce superficial rewrites of one opening.
5. **Draft complete variants.** Make the claim legible before the call to action. Optimize for voluntary, relevant actions: a specific question can invite informed replies; a concrete takeaway can merit saves; a defensible framing can earn quotes or shares. Describe these as reader affordances, never scoring signals.
6. **Run a negative-feedback review.** Check for ambiguity, overclaiming, missing context, bait, dogpiling risk, unwanted targeting, jargon, or an invitation to low-quality replies. Rewrite or reject unsafe variants.
7. **Cite and label.** Attach `claim_ids` to every factual sentence or clause in metadata. Mark unverified planning statements as `assumption` or `hypothesis`. Do not let citations imply more than their verdict permits.
8. **Return choices and a measurement plan.** Deliver the evidence ledger, hook set, publishable variants, rejected-risk notes, and a launch/measurement plan. Measure observed outcomes; do not label a result an algorithm effect without evidence.

## Output checklist

A complete result contains:

- audience, objective, language, and constraints;
- an evidence ledger with claim IDs, verdicts, freshness, and allowed wording;
- at least three distinct hooks;
- two or more complete post variants with per-assertion claim IDs;
- clearly labeled assumptions and hypotheses;
- a negative-feedback risk assessment and mitigation for each selected variant;
- a launch plan (timing rationale, reply handling, and no-spam distribution boundaries); and
- a measurement plan with baseline, observation window, metrics, and limits on causal conclusions.

Use the JSON shapes in `docs/agent-contract.md` for tool-facing work.

## Invocation examples

### Evidence-led current-system post

```text
/x-post-optimizer
Audience: open-source engineers who think the public X repository exposes a runnable full ranker.
Goal: correct the misconception and invite technically informed replies.
Language: English.
Claims: use only confirmed-current records from claims/claims.json.
Constraint: no performance or reach prediction.
```

Expected behavior: create distinct hooks; cite each factual claim ID; state any limitations as facts only when supported; invite readers to compare public and production boundaries without claiming an engagement benefit.

### Korean adaptation with uncertainty preserved

```text
/x-post-optimizer
Audience: Korean ML practitioners.
Goal: explain why public source cannot yield a deterministic content score.
Language: Korean.
Claims: use the supplied claim IDs only; retain their verdicts in metadata.
Constraint: frame unavailable inputs as limits, not as a hidden-weight theory.
```

Expected behavior: produce Korean variants while retaining the English claim IDs and verdicts in the structured output. A claim marked `inferred` remains an inference in Korean.

### Review an existing draft

```text
/x-post-optimizer review
Draft: "This format gets a 3x boost on X—try it today."
Goal: evidence and negative-feedback review.
```

Expected behavior: reject the unsupported numeric and guaranteed-outcome language, identify missing claim IDs, and offer evidence-bounded replacements only for assertions backed by fresh registry records.
