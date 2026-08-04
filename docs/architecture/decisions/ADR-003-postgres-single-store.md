# ADR-003 — PostgreSQL is the single authoritative store; Firestore is retired

**Status:** Accepted (team answer, 2026-08-03) · **Deciders:** @aalind, @cohen

## Context

`development/database/TODO.md` says "PostgreSQL confirmed" — yet the only data actually being persisted anywhere today goes to **Firestore**, via `firestore_upload.py` on `origin/cohen-working` (commit 2026-08-02). The de-facto system contradicted the de-jure decision; the team confirmed Postgres.

The data is strongly relational: events ↔ sector impacts ↔ company impacts ↔ explanations, scores-per-company-over-time, watchlists — joins, constraints, and provenance chains that document stores make painful.

## Options

1. **Postgres for everything; migrate the transcript flow off Firestore.**
2. All-in Firebase (Firestore + Firebase Auth) — least ops, but the relational impact-flow model fights document shape, and "PostgreSQL confirmed" gets overturned silently.
3. Both (Postgres app data + Firestore raw docs) — two consoles, two clients, two failure modes to explain in the M5 writeup, for zero benefit at demo scale.

## Decision

**Option 1.** Managed Postgres 16 (Railway). Cohen's transcript pipeline writes to the `raw_documents` table (schema in [data-flows.md](../data-flows.md)) instead of Firestore; `firestore_upload.py` and the `firebase_admin` dependency are deleted after migration. Migrations via Alembic under the rules in `database/migrations/TODO.md` (immutable, reversible, both directions tested).

## Consequences

- One store, one backup story, one mental model; `pg_dump` is the whole disaster-recovery and data-portability plan at this scale.
- The `check_status`/`update_status` JSON files in Cohen's scraper (whose TODOs literally say "migrate to a SQL database") become columns on `raw_documents` (`processed_at`) and per-item state — deleting a whole class of file-locking bugs.
- Cost: one Firestore→Postgres porting task (~a day: the uploader is 100 lines) plus removing GCP credentials from the env story.
- Redis explicitly not added (see ADR-007).
