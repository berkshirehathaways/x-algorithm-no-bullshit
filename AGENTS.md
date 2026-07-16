# Agent Instructions

This repository uses an evidence-first publishing contract. Treat `claims/claims.json` as the authoritative local claim registry before drafting, reviewing, translating, or adapting any X post.

## Required procedure

1. Read `claims/claims.json` and resolve every factual statement to one or more claim IDs.
2. Preserve each claim's verdict exactly. Valid verdicts are `confirmed-current`, `legacy-only`, `inferred`, `unsupported`, `unknown`, and `contradicted`.
3. Attach claim IDs to factual statements in the draft metadata and review output. Do not silently convert a verdict into stronger language.
4. State assumptions separately from facts and label them as assumptions or hypotheses.
5. Check the registry's source date, revision, and any freshness metadata before use. If evidence is absent, stale, missing a verdict, or cannot be resolved to a claim ID, fail closed: omit the assertion or describe the uncertainty. Do not fill gaps from memory, web folklore, old Twitter sources, or plausible inference.
6. Describe `legacy-only` claims as historical. Never present them as behavior of the current X system.

## Publication limits

Do not invent reach scores, rankings, engagement bonuses, or numeric weights. Public source cannot deterministically score a post: live weights, user context, production models, and experiments are unavailable. Do not promise virality or results.

Do not produce harassment, spam, engagement pods, deceptive bait, fabricated citations, or instructions to manipulate users or platform systems. A provocative claim is acceptable only when its evidence and uncertainty travel with it.

## Deliverable format

Use the stable request/response contract in `docs/agent-contract.md`. For human-readable work, include: audience and goal, distinct hook variants, cited claim IDs, labeled assumptions, negative-feedback review, final variants, and a launch and measurement plan. English is the source language; Korean adaptations must preserve claim IDs, verdicts, and uncertainty rather than translate them away.
