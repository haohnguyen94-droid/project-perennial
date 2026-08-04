# ADR-004 — Hourly batch pipeline; requests never block on third parties

**Status:** Accepted (cadence: team answer 2026-08-03) · **Deciders:** whole team

## Context

The repo contained three incompatible freshness stories: "pull every N minutes" and Confidence Score "update near-real-time when inputs change" (`development/backend/src/services/TODO.md`) vs "Runs daily at 9:00am via scheduler/cron.py" (every fetcher header on `origin/hong-working`). The team answered: **hourly**.

Free-tier quotas bound what's honest: FMP 250 req/day (`fmp.py` header), news providers ~100 req/day. "Near-real-time" was never achievable on this budget.

## Options

1. **Hourly batch for user-visible content; daily for heavy fetchers; no request-path fetching.**
2. Near-real-time (webhooks/streaming + score invalidation) — 100× the complexity, impossible on free quotas, invisible benefit to personas who check an app a few times a day.
3. Daily-only (Hao's original cadence) — contradicts the team's answer; events feel stale by evening.
4. Fetch-on-demand in the request path — couples user latency and uptime to six third parties; rejected on principle (the load-bearing rule in [overview.md](../overview.md) §3).

## Decision

**Option 1.**
- **Hourly:** news fetch → event build → impact flows → sentiment → scores → buckets (LLM stages hash-gated so unchanged content costs nothing).
- **Daily:** fundamentals, 52-week ranges, ARK/Congress/insider consensus fetchers (keeping the 9am cadence their code documents), retention sweeps.
- **Never synchronous with a user request.** The API serves what the last run produced, labeled `data_as_of`.

## Consequences

- User-facing latency is pure Postgres reads — fast and boringly reliable; third-party outages degrade freshness, never availability.
- The UI must be honest about staleness (`data_as_of` in bundles; "as of" on score breakdowns) — cheaper than pretending to be live.
- Quota math: hourly news+quotes fits budgets only with batched endpoints and per-source budget tables enforced in the clients; if a budget binds, news drops to 2-hourly (accepted degradation, build-plan.md risk #2).
- If real-time is ever truly wanted (post-MVP), the seam is the pipeline trigger — nothing in the schema assumes batch.
