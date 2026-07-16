<p align="center">
  <img src="assets/hero.svg" alt="X Algorithm: No Bullshit — The source is public. The knobs aren't." width="100%">
</p>

<h1 align="center">X Algorithm: No Bullshit</h1>

<p align="center">
  <strong>The source is public. The knobs aren't.</strong><br>
  Evidence-checked claims and an agent skill for X's May 2026 For You release.
</p>

<p align="center">
  <a href="https://github.com/berkshirehathaways/x-algorithm-no-bullshit/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/berkshirehathaways/x-algorithm-no-bullshit/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/berkshirehathaways/x-algorithm-no-bullshit/releases/latest"><img alt="Release" src="https://img.shields.io/github/v/release/berkshirehathaways/x-algorithm-no-bullshit?color=b680ff"></a>
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-6cf5d2"></a>
  <a href="claims/claims.json"><img alt="19 evidence receipts" src="https://img.shields.io/badge/evidence-19%20source--pinned%20claims-b680ff"></a>
</p>

<p align="center">
  <a href="README.ko.md">한국어</a> ·
  <a href="claims/claims.json">Claim registry</a> ·
  <a href="skills/x-post-optimizer/SKILL.md">Agent skill</a> ·
  <a href="docs/launch-kit.md">Launch kit</a>
</p>

---

A lot of “X algorithm” advice commits the same category error: it puts **2023 numeric weights** beside the **2026 Phoenix/Grok architecture** and presents the combination as current fact.

This repository makes that move difficult. Every claim receives a commit-pinned source and one explicit verdict:

`confirmed-current` · `legacy-only` · `inferred` · `unsupported` · `unknown` · `contradicted`

No anonymous growth lore. No fake 0–100 virality score. No pretending a public mini model is the live personalized ranker.

## The 60-second version

| Claim | Verdict | Receipt |
| --- | --- | --- |
| The current `RankingScorer` combines **22 named Phoenix score terms**. | `confirmed-current` | [`ranking_scorer.rs` L12–L34, L146–L170](https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L12-L34) |
| Those weights are loaded from runtime feature-switch parameters. | `confirmed-current` | [`ranking_scorer.rs` L41–L66](https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L41-L66) |
| The public source establishes the live numeric values of those weights. | `unknown` | The bounded public snapshot shows runtime lookups, not their live values. |
| “Reply-engaged-by-author = 75, therefore replies are 150× likes today.” | `legacy-only` | [That table is explicitly dated April 5, 2023](https://github.com/twitter/the-algorithm-ml/blob/b85210863f7a94efded0ef5c5ccf4ff42767876c/projects/home/recap/README.md#L26-L40). |
| The released checkpoint is the production model. | `contradicted` | [Phoenix calls it a frozen mini model and says production is larger and continuously trained](https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/phoenix/README.md#L27-L31). |
| The public docs agree on the mini-model dimensions. | `contradicted` | [Top-level: 256-dim/2-layer](https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L26-L32); [Phoenix: 128-dim/4-layer](https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/phoenix/README.md#L27-L31). |

The 19 machine-readable records live in [`claims/claims.json`](claims/claims.json); browse the generated [`claim index`](claims/README.md).
## Share the receipts

The cards are generated from the registry, not hand-maintained screenshots.

<p align="center">
  <img src="assets/cards/weights-runtime.svg" alt="Live numeric ranking weights are unknown from the public source" width="32%">
  <img src="assets/cards/reply-75-legacy.svg" alt="The 75 versus 0.5 table is April 2023 legacy context" width="32%">
  <img src="assets/cards/score-terms.svg" alt="RankingScorer consumes 22 named score terms" width="32%">
</p>

Regenerate them with `python scripts/generate_cards.py`.

## Use the evidence CLI

```bash
git clone https://github.com/berkshirehathaways/x-algorithm-no-bullshit.git
cd x-algorithm-no-bullshit
python -m pip install --no-deps -e .

xnb validate
xnb claims reply
xnb show current-numeric-ranking-weights
xnb audit "External links always kill reach: https://example.com" --has-image
```

`xnb audit` intentionally returns **no virality score**. A draft does not reveal the live weights, viewer context, production checkpoint, candidate set, or active experiments. The command reports what is sourced, what is legacy, and what remains a hypothesis.

```text
NO VIRALITY SCORE — the public source does not expose the live knobs.

[confirmed-current] X's public ranker predicts multiple viewer actions ...
[unknown] No numeric score is produced because live inputs are unavailable ...
[unsupported] A universal 2026 outbound-link penalty is not established ...
```

## Give the workflow to an agent

The canonical skill is [`skills/x-post-optimizer/SKILL.md`](skills/x-post-optimizer/SKILL.md). It makes an agent:

1. resolve every factual assertion to a claim ID;
2. preserve current, legacy, inferred, and unknown evidence boundaries;
3. draft at least three materially different hooks;
4. optimize reader affordances without inventing ranking bonuses;
5. review negative-feedback risk; and
6. return variants plus a measurable launch experiment.

Copy it into an Agent Skills-compatible project:

```bash
mkdir -p .agents/skills
cp -R skills/x-post-optimizer .agents/skills/
```

Claude Code plugin installation:

```text
/plugin marketplace add berkshirehathaways/x-algorithm-no-bullshit
/plugin install x-algorithm-no-bullshit@x-algorithm-no-bullshit
```

Example request:

```text
Use x-post-optimizer.
Audience: ML engineers who believe the 75/0.5 table is current.
Goal: write a sharp correction that people can verify themselves.
Constraint: cite claim IDs; no reach prediction or rage bait.
```

Tool adapters can use the stable JSON request/response shapes in [`docs/agent-contract.md`](docs/agent-contract.md).

## What the public release can and cannot tell you

### It can show

- in-network Thunder and out-of-network Phoenix candidate paths;
- 22 values combined by the current ranking scorer;
- negative-action terms including not-interested, block, mute, report, and not-dwelled;
- author-diversity attenuation and configurable out-of-network weighting;
- candidate-isolation attention masking;
- pre-scoring filters such as previously seen and previously served; and
- a `quality_score >= 0.4` positive threshold in the public banger screen.

### It cannot give you

- the current numeric production weights;
- a deterministic score for arbitrary post text;
- the hidden qualitative rubric behind the banger score;
- the production model, live user context, training stream, or experiments; or
- a guarantee of reach, engagement, virality, or feed placement.

Phoenix is documented as a runnable public pipeline. The bounded snapshot does not establish equivalent standalone reproducibility for the complete Grox/Rust production path.

## Evidence that rots gets caught

The registry is pinned to upstream commit [`0bfc279`](https://github.com/xai-org/x-algorithm/tree/0bfc2795d308f90032544322747caacd535f75ae). A scheduled GitHub Action runs:

```bash
python scripts/check_upstream.py
python scripts/verify_sources.py
```

When upstream moves, CI reports the old and new SHAs instead of silently letting screenshots become “current truth.” Offline tests enforce registry metadata, unique claim IDs, verdict vocabulary, full commit pins, valid line ranges, and source URLs.

## Repository map

```text
claims/                         machine-readable claims + schema + index
contracts/                      JSON Schemas and conformance examples
skills/x-post-optimizer/        vendor-neutral agent workflow
src/xnb/                        zero-dependency evidence CLI
docs/agent-contract.md          versioned adapter contract
docs/launch-kit.md              X, HN, Reddit, and Product Hunt copy
scripts/check_upstream.py       upstream drift detector
scripts/generate_cards.py       deterministic claim-card generator
assets/cards/                   shareable evidence cards
assets/hero.svg                 repository hero artwork
```
## Related work

These projects solve adjacent problems; this repository is the conservative provenance layer.

| Project | Strength | This project's different lane |
| --- | --- | --- |
| [`cclank/x-algorithm-wiki`](https://github.com/cclank/x-algorithm-wiki) | Deep source-anchored architecture wiki | Atomic machine-readable claims and explicit fail-closed verdicts |
| [`AytuncYildizli/reach-optimizer`](https://github.com/AytuncYildizli/reach-optimizer) | Composer UI, forecasts, and calibration | No false-precision score; current-vs-legacy receipts |
| [`sheeki03/x-algo-tweet-scorer`](https://github.com/sheeki03/x-algo-tweet-scorer) | Explicit verified/estimated/heuristic labels | Immutable claim-level provenance and no numeric output |
| [`ceoguy/x-algorithm-skill`](https://github.com/ceoguy/x-algorithm-skill) | Rich Claude workflow and examples | Vendor-neutral, conservative claim resolution |

## Independent, deliberately

This project is not affiliated with X, xAI, or Twitter. It analyzes public source under its respective licenses and publishes original metadata, commentary, and tooling under MIT. It does not reproduce the live ranker.

Found a bad receipt? Open a correction with a pinned primary-source URL and the verdict it changes.

**Star it to keep the receipts findable the next time a 2023 screenshot is sold as a 2026 secret.**

## Primary sources

- Current public release: [`xai-org/x-algorithm@0bfc279`](https://github.com/xai-org/x-algorithm/tree/0bfc2795d308f90032544322747caacd535f75ae)
- Legacy service source: [`twitter/the-algorithm`](https://github.com/twitter/the-algorithm)
- Legacy Heavy Ranker weights: [`twitter/the-algorithm-ml`](https://github.com/twitter/the-algorithm-ml)
