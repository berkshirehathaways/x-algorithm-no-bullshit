# Claim index

Generated from `claims/claims.json`; do not edit by hand.

Regenerate: `python3 scripts/generate_cards.py`

## confirmed-current

### `weighted-multi-action-ranking`

**Claim:** The current For You ranker combines predicted engagement actions into a weighted final score.

**Practical implication:** Optimize for a mix of valuable predicted actions, not one public engagement metric.

**Evidence:** The current README states that the final score is a weighted combination of predicted engagements and gives the weighted-sum formula.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — README.md:L286-L292](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L286-L292>)

### `current-ranker-22-score-terms`

**Claim:** The current RankingScorer combines 22 named Phoenix score terms.

**Practical implication:** Do not reduce current ranking to likes or reuse a shorter action list as exhaustive.

**Evidence:** ScoringWeights declares 22 score-term weights and compute\_weighted\_score applies the corresponding 22 Phoenix score fields.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L12-L34](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L12-L34>)
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L146-L170](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L146-L170>)

### `runtime-ranking-weights-not-public-values`

**Claim:** The current RankingScorer reads its score-term weights from runtime feature-switch parameters.

**Practical implication:** Parameter names in public source are not a current numeric weight table.

**Evidence:** ScoringWeights is constructed from Params and the server evaluates feature switches per request.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L41-L66](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L41-L66>)
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/server.rs:L138-L164](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/server.rs#L138-L164>)

### `author-diversity-attenuates-repetition`

**Claim:** Author diversity attenuates repeated-author scores within a feed response.

**Practical implication:** Repeated posting by one author is not a reliable way to occupy multiple top positions.

**Evidence:** The current RankingScorer sorts by weighted score and applies a configurable position-dependent multiplier to repeated authors.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L186-L217](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L186-L217>)

### `oon-weighting`

**Claim:** Out-of-network candidates receive a configurable multiplicative score adjustment.

**Practical implication:** A post can be relevant and still be affected by its in-network versus out-of-network route.

**Evidence:** The ranking scorer computes an effective OON weight and multiplies scores for candidates marked out-of-network.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L220-L238](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L220-L238>)
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L263-L280](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L263-L280>)

### `candidate-isolation`

**Claim:** Phoenix masks candidate-to-candidate attention while retaining each candidate's self-attention.

**Practical implication:** A candidate's model score is designed not to depend on the other candidates batched beside it.

**Evidence:** The attention-mask implementation zeros the candidate block and restores its diagonal; README documents the resulting isolation.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — phoenix/grok.py:L63-L69](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/phoenix/grok.py#L63-L69>)

### `frozen-mini-model-is-not-production-proof`

**Claim:** The released Phoenix checkpoint is a frozen mini model, while production uses a larger model trained continuously.

**Practical implication:** Use the bundled model for reproducible demonstrations, not as a production-equivalent ranker.

**Evidence:** The Phoenix README explicitly distinguishes the smaller frozen release from the larger continuously trained production model.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — phoenix/README.md:L27-L31](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/phoenix/README.md#L27-L31>)

### `banger-threshold-and-rubric`

**Claim:** The public banger initial screen marks quality scores greater than or equal to 0.4 as positive.

**Practical implication:** The threshold is observable, but it is not itself a content recipe.

**Evidence:** The classifier records quality\_score and sets banger\_initial\_positive when score \>= 0.4.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — grox/classifiers/content/banger\_initial\_screen.py:L102-L129](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/grox/classifiers/content/banger_initial_screen.py#L102-L129>)

### `previously-seen-filtering`

**Claim:** The documented current pipeline filters previously seen posts and posts already served in the session before scoring.

**Practical implication:** Repeated exposure is constrained; raw engagement alone does not guarantee repeat delivery.

**Evidence:** README lists PreviouslySeenPostsFilter and PreviouslyServedPostsFilter among pre-scoring filters.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — README.md:L300-L312](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L300-L312>)

### `in-network-and-oon-sourcing`

**Claim:** Current For You sourcing combines followed-account posts with ML-retrieved global-corpus posts.

**Practical implication:** Follower reach and recommendation reach are separate candidate paths.

**Evidence:** README defines Thunder as in-network and Phoenix Retrieval as out-of-network, then says they are ranked together.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — README.md:L47-L55](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L47-L55>)

### `negative-action-downranking`

**Claim:** The documented weighted score assigns negative actions such as block, mute, and report negative weights.

**Practical implication:** Avoidance signals can lower ranking; visible engagement alone is incomplete evidence of relevance.

**Evidence:** README explicitly states that block, mute, and report have negative weights in the weighted score.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — README.md:L286-L292](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L286-L292>)

## legacy-only

### `reply-75-or-150x`

**Claim:** The April 2023 Heavy Ranker table assigned 75.0 to reply-engaged-by-author and 0.5 to favorite.

**Practical implication:** The derived 150× ratio describes that dated table, not the current 2026 RankingScorer.

**Evidence:** The source explicitly dates the published weights April 5, 2023; the current scorer resolves a different set of runtime parameters.

**Sources:**
- [twitter/the-algorithm-ml @ b8521086 — projects/home/recap/README.md:L26-L40](<https://github.com/twitter/the-algorithm-ml/blob/b85210863f7a94efded0ef5c5ccf4ff42767876c/projects/home/recap/README.md#L26-L40>)

### `tweepcred-threshold`

**Claim:** The legacy Follow Recommendations LowTweepCredFollowStore used a TweepCred threshold of 40.

**Practical implication:** Do not convert that historical, different-product threshold into a current For You eligibility rule.

**Evidence:** The legacy Follow Recommendations store defines TweepCredThreshold = 40.

**Sources:**
- [twitter/the-algorithm @ c54bec0d — follow-recommendations-service/common/src/main/scala/com/twitter/follow\_recommendations/common/stores/LowTweepCredFollowStore.scala:L12-L38](<https://github.com/twitter/the-algorithm/blob/c54bec0d4e029fe34926ef3258a86ccacc0d0182/follow-recommendations-service/common/src/main/scala/com/twitter/follow_recommendations/common/stores/LowTweepCredFollowStore.scala#L12-L38>)

## unsupported

### `universal-link-penalty`

**Claim:** The current public ranking source establishes a universal external-link penalty.

**Practical implication:** Do not claim that every external link is algorithmically penalized.

**Evidence:** Current documentation describes multi-action prediction and weighted ranking but does not establish a universal link penalty; absence is not proof that no contextual treatment exists.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L146-L170](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L146-L170>)

### `fixed-first-30-minute-boost`

**Claim:** The current public source establishes a fixed first-30-minute ranking boost.

**Practical implication:** Avoid presenting a universal 30-minute posting-window boost as fact.

**Evidence:** Legacy Home Mixer has a predicate for tweet age at most 30 minutes, but that does not identify a fixed boost or establish current behavior.

**Sources:**
- [twitter/the-algorithm @ c54bec0d — home-mixer/server/src/main/scala/com/twitter/home\_mixer/functional\_component/decorator/builder/HomeTweetTypePredicates.scala:L232-L234](<https://github.com/twitter/the-algorithm/blob/c54bec0d4e029fe34926ef3258a86ccacc0d0182/home-mixer/server/src/main/scala/com/twitter/home_mixer/functional_component/decorator/builder/HomeTweetTypePredicates.scala#L232-L234>)

## unknown

### `current-numeric-ranking-weights`

**Claim:** Current live numeric values for the RankingScorer weights.

**Practical implication:** Do not publish a numeric 2026 weight table as current fact.

**Evidence:** The bounded public snapshot exposes parameter lookups but no definitions or live values for those feature-switch parameters; this does not prove that no additional values exist internally.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — home-mixer/scorers/ranking\_scorer.rs:L41-L66](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/home-mixer/scorers/ranking_scorer.rs#L41-L66>)

### `banger-quality-rubric`

**Claim:** The qualitative rubric used to produce the banger quality score.

**Practical implication:** Do not reverse-engineer a guaranteed writing formula from the 0.4 cutoff.

**Evidence:** The classifier imports and renders BangerMiniVlmScreenScore from a prompt template that is not present in the bounded public tree.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — grox/classifiers/content/banger\_initial\_screen.py:L11-L64](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/grox/classifiers/content/banger_initial_screen.py#L11-L64>)

### `public-grox-orchestration-limits`

**Claim:** Standalone reproducibility of complete Grox/Rust production orchestration from the published snapshot.

**Practical implication:** Do not promise that all published components reproduce production orchestration.

**Evidence:** The README documents Phoenix as a runnable end-to-end pipeline but does not establish equivalent standalone runnability for the complete Grox/Rust production path.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — README.md:L28-L34](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L28-L34>)

## contradicted

### `readme-demo-config-contradiction`

**Claim:** The top-level and Phoenix READMEs publish one consistent mini-model configuration.

**Practical implication:** Treat public model dimensions as artifact- or document-specific until upstream reconciles them.

**Evidence:** The top-level release note describes a 256-dimension, 2-layer artifact; the Phoenix release overview describes a 128-dimension, 4-layer mini model.

**Sources:**
- [xai-org/x-algorithm @ 0bfc2795 — README.md:L26-L32](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/README.md#L26-L32>)
- [xai-org/x-algorithm @ 0bfc2795 — phoenix/README.md:L27-L31](<https://github.com/xai-org/x-algorithm/blob/0bfc2795d308f90032544322747caacd535f75ae/phoenix/README.md#L27-L31>)
