# ADR-008 — What "Affordable & Growing" / "Popular & Stable" actually mean

**Status:** 🗳️ **PROPOSED — needs a team vote.** This is the one genuinely unresolved product-architecture contradiction in the repo. · **Deciders:** whole team (it defines the product's public vocabulary)

## Context — two codebases, two definitions

| Source | Affordable & Growing | Popular & Stable |
|---|---|---|
| `development/backend/src/services/TODO.md` (homepage service) | "lower price + positive momentum" | "high market cap + steady momentum" |
| `origin/hong-working` pipeline (working code) | **ARK ETF holdings** (`ark.py`: "the 'Affordable & Growing' candidate list") | **Congress purchases + insider confirmation** (`insider.py` buckets) |

These produce different lists *and different explanations*. The buckets are the product's headline vocabulary — marketing leads with them (`assets/marketing/TODO.md`), user testing probes whether users "grasp the difference without explanation" (`testing/user-testing/TODO.md`). Ambiguity here leaks straight into the demo.

## Options

1. **Screen-based membership + consensus-as-evidence (proposed).** Bucket membership is defined by transparent screening criteria over market data (per the services TODO): A&G ≈ price below threshold ∧ positive momentum ∧ market cap below X; P&S ≈ market cap above Y ∧ volatility below Z. Hao's consensus signals (Congress buys, ARK conviction, insider clusters) become **inputs to the Confidence Score and Key Reasons** ("Members of Congress bought this stock recently", "insiders are buying") — evidence, not gatekeepers.
2. **Consensus-based membership** (ratify the pipeline): A&G = ARK holdings, P&S = Congress+insider consensus. Zero rework of Hao's code, and the lists carry a story ("smart money") — but membership explanations become second-hand ("because ARK holds it"), coverage is hostage to a third party's fund choices, and the P&S list skews to whatever Congress traded, not to "popular & stable" as a beginner reads it.
3. **Hybrid gate:** screen criteria define eligibility; consensus signals rank within the bucket. (A softer version of 1; more moving parts to explain.)

## Proposed decision

**Option 1.** Rationale: the bucket labels promise *plain-language meaning* ("Affordable & Growing not small cap" — `README.md` design principles). A screening rule is explainable in one sentence a beginner can verify; "a fund we track holds it" is not. Hao's pipeline is **not wasted** — it's re-aimed at the score/reasons layer, arguably a better home: `insider.py` already describes itself as "a SCORER not a gate."

Concrete thresholds get tuned against the seeded universe and documented in `docs/technical-specs/SCORING_FORMULA.md`; each `companies.bucket` assignment stores its explanation string alongside (explainability invariant).

## Consequences

- If the vote goes to option 2 instead: schema unchanged (`companies.bucket` + explanations still hold); the homepage service and the marketing one-liners change; screening code isn't built.
- **Not deciding is the worst outcome** — the walking-skeleton demo (build-plan M-C) hard-depends on some definition; build-plan risk #3 tracks this. Default if the vote stalls: option 1, because it matches the only definition on `main`.
