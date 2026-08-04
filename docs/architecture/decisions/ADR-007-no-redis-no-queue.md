# ADR-007 — No Redis, no message queue in v1

**Status:** Accepted (architect recommendation) · **Deciders:** @aalind

## Context

`development/database/TODO.md` suggests "add Redis caching? (recommended for Confident Score caching)". The pipeline needs scheduling; queues (Celery/RQ) are the reflexive answer.

## Reality check at demo scale (Q4/Q5)

- Reads: every hot payload is a few joined rows over ≤150 companies — sub-millisecond in Postgres. There is nothing slow to cache.
- Writes: one pipeline run per hour, minutes of work, no fan-out, no user-triggered jobs.
- The "Confident Score caching" the TODO worried about assumed near-real-time recomputation; ADR-004 removed that premise — scores are precomputed rows.

## Options

1. **Postgres + cron only.** Scheduling via Railway cron (or APScheduler in-process as fallback); stages communicate through tables; `pipeline_runs` row provides the concurrency lock.
2. Redis cache + Celery workers — two more services to run, monitor, and explain, guarding against load that doesn't exist.
3. Redis later, when measured — indistinguishable from option 1 today.

## Decision

**Option 1.** Explicitly reversing the repo's Redis lean, with the seam kept: composed read paths live in service functions, so a cache decorator (or Redis) drops in behind the same interface if p95 latency ever says so — measured first, added second.

## Consequences

- Two deployable processes total; the M5 ops story stays one paragraph.
- If a future feature needs true background jobs per user action (e.g., on-demand report generation), that's the moment to add a queue — additive, not a rework.
- Anyone proposing Redis/Celery in review must bring a latency or throughput measurement to the PR.
