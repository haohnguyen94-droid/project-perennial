# ADR-005 — Claude Sonnet, ingestion-time only, structured and hash-gated

**Status:** Accepted (model: team answer 2026-08-03) · **Deciders:** @cohen, @aalind

## Context

The explainability layer — "What Happened", "Effects Markets", per-node impact explanations, score Breakdowns, Key Reasons — is the product (`services/TODO.md` requires every output to "include the explanation string, not just the number", and anticipates summaries "likely via LLM"). The team chose **Claude Sonnet** to balance quality and price.

## Decision

1. **Model:** `claude-sonnet-5` via the official `anthropic` Python SDK. ($3/M input, $15/M output tokens; intro pricing $2/$10 through 2026-08-31.)
2. **Where:** pipeline stages only. **The API service never calls the LLM.** Content is generated once, served thousands of times; user latency and uptime never depend on Anthropic.
3. **How:**
   - **Structured outputs** (`client.messages.parse` with Pydantic schemas) for every generation — impact trees arrive as typed objects, not prose to regex.
   - **Universe-constrained prompts + referential validation:** the prompt lists the known sectors/tickers; any name outside it in the response is dropped and logged (anti-hallucination gate).
   - **Hash gating:** `events.content_hash` and `confident_scores.inputs_hash` — no input change, no LLM call.
   - **Message Batches API** for bulk regeneration (nightly breakdown refresh) at 50% price; **prompt caching** for the shared system prompt across per-event calls.
   - **Disclaimer field** attached to every AI-derived payload (repo requirement, `services/TODO.md` + `middleware/TODO.md`).
4. **What the LLM does NOT do:** compute the 0–100 score (deterministic formula in code — testable per `testing/unit/TODO.md`); classify at bulk scale if a cheaper path suffices (the team may later opt sentiment classification down to Haiku 4.5 at $1/$5 — flagged as a team cost decision, not made here); see user data (**no PII in prompts, ever** — prompts contain public market/news/transcript text only).

## Cost estimate (demo scale, labeled as estimate)

~10–20 new events/day × (~4K in + ~1.5K out) ≈ $0.40–0.80/day; score-text regen hash-gated and batched ≈ similar order. **Expect $15–40/month**; alarm threshold $2/day (build-plan.md risk #6).

## Consequences

- Quality risk concentrates in prompts — mitigated by the eval harness being the walking skeleton's exit criterion (build-plan.md §0) and a CI regression on prompt changes.
- Model swaps (Sonnet ↔ Haiku for sub-tasks, future models) are config + eval re-run — cheap to reverse.
- An Anthropic outage stalls content freshness only; the app keeps serving.
