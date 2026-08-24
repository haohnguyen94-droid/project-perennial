# Perennial — PostgreSQL Setup Outline

**Author:** @bryan · **Date:** 2026-08-23
**Companion docs:** [pipeline-and-schema-guide.md](../../docs/architecture/pipeline-and-schema-guide.md) (full DDL — the source of truth for table definitions), [data-flows.md](../../docs/architecture/data-flows.md), [ADR-003](../../docs/architecture/decisions/ADR-003-postgres-single-store.md), [ADR-007](../../docs/architecture/decisions/ADR-007-no-redis-no-queue.md), [ADR-008](../../docs/architecture/decisions/ADR-008-bucket-semantics.md)

This document is two things: **(1)** a record of the repo deep-dive that grounds the plan — what I examined, what I found, and what changed since the architecture docs were written — and **(2)** the step-by-step outline for standing up Postgres, from local docker to production Railway, with reasoning at each step.

It deliberately does **not** duplicate the ~300-line DDL that already lives in
[pipeline-and-schema-guide.md §1.2](../../docs/architecture/pipeline-and-schema-guide.md).
Two copies of a schema drift apart; this doc references that one and lists only
the **amendments** the deep-dive surfaced (§3 below).

---

## 1. Deep dive — what I examined and what I found

### 1.1 Repo state

- `main` (and `bryan-working`, one commit ahead) contain **no application code** —
  a folder scaffold with per-folder `TODO.md` files, plus the full architecture
  doc set under `docs/architecture/` (overview, data-flows, stack decision,
  build plan, 10 ADRs, and the database/pipeline implementation guide).
- The working code lives on **sibling branches**, and the schema must land what
  that code actually emits:

| Branch | What's on it | DB relevance |
|---|---|---|
| `origin/hong-working` | Consensus watchlist pipeline: `fetchers/fmp.py` (Congress trades), `ark.py` (ARK holdings), `insider.py` (SEC Form 4), **`short_interest.py` (FINRA — new, post-dates the architecture docs)**, `consensus.py` aggregator, `scheduler/cron.py`, `.env.example` | These currently write JSON files to `development/database/local_data/`; their headers say "Replace with write_to_db() once DB is set up". They are the writers for `consensus_signals`. |
| `origin/cohen-working` | YouTube transcript pipeline (`api/youtube.py`, yt-dlp) + `middleware/firestore_upload.py` (keyed by video ID), plus a Vite React frontend | The Firestore uploader is retired per ADR-003; transcripts land in `raw_documents` with `provider='youtube'`, `external_id=<video_id>`. |
| `origin/aalind-working`, `origin/cohen-cloudflare` | Not DB-relevant at inspection time | — |

### 1.2 Findings that change the schema (deltas vs. the architecture docs)

These are things the docs (written 2026-08-03) could not have known because the
code moved after they were written:

1. **A fourth consensus signal type exists.** `short_interest.py` on
   `hong-working` pulls the FINRA Consolidated Equity Short Interest API.
   The guide's `consensus_signals.signal_type` CHECK only allows
   `('congress_trade','ark_holding','insider_buy')` — a FINRA row would be
   **rejected at insert**. Amendment #1 below adds `'short_interest'`.
2. **`consensus.py` has already implemented concrete bucket semantics**:
   `popular_stable` = Congress-purchase discovery with market cap > $10B;
   `affordable_growing` = ARK discovery with market cap ≤ $10B; plus an
   **`unresolved`** bucket for failed market-cap lookups. This is essentially
   ADR-008 **option 2** (consensus-based membership) shipped as working code,
   while the ADR *proposes* option 1 (screen-based). The contradiction the ADR
   flags is now sharper — the vote is more urgent, not less. The schema is
   deliberately neutral (`companies.bucket` + `bucket_explanation` hold under
   either outcome), so **DB setup does not block on the vote** — but the
   `buckets` pipeline stage does.
3. **New secrets to provision:** `FINRA_API_URL`, `FINRA_CLIENT_ID`,
   `FINRA_CLIENT_SECRET`, `FINRA_API_KEY` (from the consensus README), beyond
   the FMP/Finnhub/YouTube keys in `.env.example`. Also `TWITTER_BEARER_TOKEN`
   appears in `.env.example` — if X/Twitter sentiment ships, it's just another
   `raw_documents.provider` value; `provider` being free `text` (not a CHECK)
   absorbs this with zero migration. That looseness is now validated design.
4. **`DATABASE_URL` is already the agreed env var name** (in `.env.example` on
   `hong-working`) — the Alembic/SQLAlchemy config below reads it verbatim.

### 1.3 Decisions inherited (not re-litigated here)

| Decision | Source | Consequence for setup |
|---|---|---|
| Postgres 16, single authoritative store; Firestore retired | ADR-003 | One `docker-compose` service locally; one Railway Postgres in prod; `pg_dump` is the DR plan |
| No Redis, no queue | ADR-007 | Nothing else to provision; pipeline stages hand off through tables |
| Alembic migrations — immutable, reversible, both directions tested in CI | `migrations/TODO.md` + overview §5 | CI job in §7; conventions in §4 |
| `uuid` PKs (`gen_random_uuid()`), `timestamptz` UTC, `text`+CHECK not PG enums, `numeric` never `float`, every FK indexed, explicit `as_of_date` columns | guide §1.1 | Applied throughout the DDL; enforced in review |
| API writes user tables only; pipeline writes content tables only (single exception: `watchlist_items.has_new_event`) | data-flows §2 | §5 makes this a **mechanical guarantee** via two DB roles, not a code-review convention |
| Scale honesty: 50–150 tickers, <100 users | overview (Q4/Q7) | No partitioning, no read replicas, minimal indexes; `raw_documents` is the only table with a real growth story |

---

## 2. The schema at a glance (defined in full in the guide)

Seven tiers, in dependency order — this is also the migration order:

| Tier | Tables | Written by |
|---|---|---|
| 0 — reference | `sectors`, `companies` | pipeline |
| 1 — users & auth | `users`, `refresh_tokens`, `user_interests`, `user_notification_preferences`, `watchlist_items` | API only |
| 2 — operations | `pipeline_runs` | pipeline |
| 3 — ingestion staging | `raw_documents`, `consensus_signals` | pipeline (pipeline-read only) |
| 4 — market time series | `company_price_snapshots`, `company_financials` | pipeline |
| 5 — insight content | `events`, `event_sector_impacts`, `event_company_impacts`, `event_sources` | pipeline (✦ LLM fields) |
| 6 — scoring & sentiment | `confident_scores`, `sentiment_pulses`, `why_this_company` | pipeline |

Load-bearing shape: `events → event_sector_impacts → event_company_impacts
(via_sector_id)` **is** the Event Impact Flow — the product's differentiator is
a two-level fan-out you can query in one round trip. Everything in tiers 5–6
must be traceable back to `raw_documents` / `pipeline_runs` (provenance chain,
data-flows §4).

---

## 3. Amendments to the guide's DDL (apply in migration 001)

Each of these folds a later discovery or a guide-footnote into the initial
migration, so we never ship a migration we already know is wrong.

1. **`consensus_signals.signal_type`** — CHECK becomes
   `('congress_trade','ark_holding','insider_buy','short_interest')`.
   *Reason:* finding #1 above; the FINRA fetcher exists today.
   `dedupe_key` for short interest = `sha256(ticker | settlement_date)` —
   FINRA publishes one figure per ticker per settlement cycle, so that pair
   identifies the real-world observation, same pattern as the Congress-trade
   key in guide §2.5.
2. **`events.published boolean NOT NULL DEFAULT false`** + partial index
   `(published, published_at DESC)` — in the initial DDL, not a later ALTER.
   *Reason:* guide §2.11 adds this as the validate-stage gate ("a malformed
   impact tree is invisible rather than embarrassing"). We know we want it;
   creating `events` without it just schedules a second migration for no
   benefit. The API filters `WHERE published` from day one.
3. **Extensions first:** `CREATE EXTENSION IF NOT EXISTS citext;` and
   `CREATE EXTENSION IF NOT EXISTS pg_trgm;` as the first operations of
   migration 001. *Reason:* `users.email` is `citext`; the guide's
   `companies_search_idx` (trigram GIN over `ticker || ' ' || name`) fails
   without `pg_trgm`. Both ship with stock Postgres 16 and Railway allows
   both — verified constraint, not hope. (`gen_random_uuid()` is built into
   PG 13+; no `pgcrypto` needed.)
4. **`updated_at` maintained by SQLAlchemy (`onupdate=func.now()`), no
   triggers** — the guide's call, restated here because it's a setup-time
   temptation: trigger-based `updated_at` is invisible to a teammate reading
   the models. One place to look wins at team scale.

Everything else in guide §1.2 is adopted verbatim — including the choices that
superseded data-flows.md (explicit `as_of_date` over `captured_at::date`
unique indexes, because the cast depends on session `TimeZone` and an
expression index over it is not stable; and the two-nullable-FKs + XOR CHECK
watchlist over a polymorphic `(target_type, target_id)`, because a polymorphic
id can't have a foreign key and silently strands rows when a company is
deleted).

---

## 4. Setup outline — step by step

### Step 0 — Local Postgres via docker-compose

`development/docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:16-alpine        # ADR-003 pins PG 16; alpine for size
    environment:
      POSTGRES_USER: perennial
      POSTGRES_PASSWORD: perennial   # local only; prod creds live in Railway
      POSTGRES_DB: perennial
    ports: ["5433:5432"]   # host 5433: a native PostgreSQL install often owns 5432
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U perennial"]
      interval: 5s
      timeout: 3s
      retries: 10
volumes:
  pgdata:
```

Local `.env` (untracked; extend `.env.example` from `hong-working` so there is
one canonical example file):

```
DATABASE_URL=postgresql+psycopg://perennial:perennial@localhost:5433/perennial
```

*Reasoning:* matching the prod engine exactly (PG 16) is the whole point of
docker here — SQLite-for-dev would hide `citext`, `jsonb`, partial-index, and
`ON CONFLICT` behavior we depend on. The healthcheck lets `make db-upgrade`
wait on readiness instead of racing the container.

### Step 1 — Alembic scaffolding

```
development/backend/
  alembic.ini
  migrations/
    env.py            # reads DATABASE_URL from the environment — never hardcoded
    versions/
```

Non-negotiable configuration:

- **Naming convention** on SQLAlchemy `MetaData` (ix/uq/ck/fk/pk templates) so
  every constraint gets a deterministic name. *Reason:* unnamed constraints get
  auto-generated names that differ per database, which makes the *reversible
  migrations* rule (`migrations/TODO.md`) impossible to honor — you can't drop
  a constraint you can't name.
- `compare_type=True`, `compare_server_default=True` in `env.py` so
  autogenerate catches column-type drift.
- Autogenerate is a **draft generator, not an author**: every migration is
  hand-reviewed before commit (guide: "autogenerate + hand-review").
  CHECK constraints and partial indexes are exactly what autogenerate misses.
- Migration files: `YYYYMMDDHHMMSS_short_description.py`, immutable once
  merged, every one reversible (`migrations/TODO.md`, adopted verbatim).

### Step 2 — Migration 001: extensions + Tiers 0, 2, 3, 5

Create, in order: extensions (§3.3) → `sectors` → `companies` →
`pipeline_runs` → `raw_documents` → `consensus_signals` (with §3.1) →
`events` (with §3.2) → `event_sector_impacts` → `event_company_impacts` →
`event_sources`.

*Reasoning:* this is the guide's build-order step 1 — the minimum schema for
the walking skeleton (news → events → impact flow), which is the differentiator
and therefore the thing to de-risk first. Order within the migration follows FK
dependencies; `downgrade()` drops in exact reverse.

### Step 3 — Migration 002: Tiers 4 + 6

`company_price_snapshots`, `company_financials`, `confident_scores`,
`sentiment_pulses`, `why_this_company`. Lands with the `market_data` and
`scoring` stages (build-order step 6).

### Step 4 — Migration 003: Tier 1 (users & auth)

`users`, `refresh_tokens`, `user_interests`, `user_notification_preferences`,
`watchlist_items`. Handed to Hong (Security Lead) with the schema frozen —
argon2id hashing and token flows are theirs per ADR-006; the tables are ours.

*Reasoning for splitting 001/002/003 rather than one mega-migration:* each
migration lands with the code that uses it, so a rollback maps to a feature,
not to "the whole database." The cost (three files instead of one) is nil.

### Step 5 — Seeds (`development/database/seeds/`)

Per `seeds/TODO.md`: 3 persona users, ~50 companies across 5 sectors, ~20
events with full impact trees and 2–3 sources per type, sample watchlists.

- One `seed.py` entrypoint, **idempotent** — every insert is
  `ON CONFLICT DO UPDATE` on the same natural keys the pipeline uses
  (`companies.ticker`, `events.content_hash`, …). Running twice changes
  nothing; the seeds convention demands it, and it doubles as the first test
  of the upsert keys the pipeline will rely on.
- **Run the guide §2.11 data-quality checks against the seeds in CI.** Seeds
  that fail our own "every event has branches, every branch has leaves,
  every explanation ≥ 20 chars" gates are seeds that make the demo look
  broken. "Believable" becomes mechanical, not aesthetic.

### Step 6 — Make targets (developer ergonomics)

```
make db-up        # docker compose up -d db (waits on healthcheck)
make db-upgrade   # alembic upgrade head
make db-downgrade # alembic downgrade -1
make db-seed      # python -m database.seeds.seed
make db-reset     # drop + recreate + upgrade + seed  (local only, guarded)
make db-psql      # psql into the local DB
```

*Reasoning:* five people, mixed familiarity with Alembic. The commands anyone
types more than twice get a make target, or they get typed wrong.

---

## 5. Roles & permissions — making the writer invariant mechanical

Data-flows §2 states the system's core invariant: **the API never writes
content tables; the pipeline never writes user tables.** As a code-review rule
that decays; as Postgres GRANTs it can't:

```sql
CREATE ROLE perennial_api   LOGIN PASSWORD '…';
CREATE ROLE perennial_pipe  LOGIN PASSWORD '…';

-- API: full ownership of user tables, read-only on content
GRANT SELECT, INSERT, UPDATE, DELETE ON users, refresh_tokens, user_interests,
  user_notification_preferences, watchlist_items TO perennial_api;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO perennial_api;

-- Pipeline: full ownership of content tables, no access to user PII…
GRANT SELECT, INSERT, UPDATE, DELETE ON sectors, companies, pipeline_runs,
  raw_documents, consensus_signals, company_price_snapshots, company_financials,
  events, event_sector_impacts, event_company_impacts, event_sources,
  confident_scores, sentiment_pulses, why_this_company TO perennial_pipe;
-- …except the two sanctioned touchpoints:
GRANT SELECT ON user_interests TO perennial_pipe;          -- personalization ranking
GRANT SELECT, UPDATE ON watchlist_items TO perennial_pipe; -- has_new_event flag
```

The retention sweep (hard-deleting soft-deleted users) runs as `perennial_api`
credentials in the daily job, since user-row deletion is API-domain work.

*Reasoning:* this costs one migration and two Railway env vars
(`DATABASE_URL_API`, `DATABASE_URL_PIPELINE`), and it converts the
architecture's central discipline from "we promise" into "the database
refuses." It also means a pipeline bug can never touch `password_hash`.
At demo scale this is optional — but it's the single cheapest piece of
defense-in-depth available, and the near-miss with committed credentials on
`cohen-working` says this team benefits from mechanical guardrails.
**If it causes friction in week one, collapse to a single role and revisit —
the invariant matters more than the enforcement mechanism.**

---

## 6. Production (Neon — provisioned 2026-08-24)

> **Reality supersedes the original plan here.** overview.md §4 proposed
> Railway for compute + DB; Railway's free plan turned out to block resource
> provisioning entirely, and the team chose **Neon's free tier** for the
> database instead (hosting was always the cheap-to-reverse decision).
> Compute hosting is still open — decided when the API actually deploys;
> Railway/Render remain candidates, and moving this DB anywhere later is a
> `pg_dump` restore.

**What exists:**

| | |
|---|---|
| Project | `perennial` (id `floral-dew-49584719`), org: Bryan's personal Neon org |
| Engine | PostgreSQL **16.15** (same minor as local Docker), aws-us-east-1 |
| Schema | Migration 001 applied (`alembic_version` = `e12d2abbc333`); `citext` + `pg_trgm` confirmed |
| Credentials | Connection string in the Neon console (Dashboard → project → Connect). **Never committed, never pasted in Discord.** Rotate from the console if ever exposed. |

**Free-tier characteristics to know (they shape operations):**

1. **Compute autosuspends when idle** — the first query after a quiet period
   takes ~1s extra while it wakes. Fine at demo scale; don't mistake it for
   an outage. (The hourly pipeline will keep it warm during the day anyway.)
2. **512 MB logical size limit** — plenty for 150 tickers (~tens of MB), but
   it makes the `raw_documents` body-truncation + 90-day retention rules
   (§8) *mandatory hygiene*, not nice-to-haves.
3. **~6h point-in-time history on free tier** — so the **weekly `pg_dump` to
   a team-accessible location is the real backup**, and one restore drill
   before user testing is non-negotiable (a dump we've restored once is a
   plan; one we've never restored is a hope).

**Rules that stand regardless of host:**

- Alembic runs `upgrade head` as a **release step** before new app code
  serves traffic — never auto-migrate on app import.
- Nobody develops against the prod URL; local Docker is for development,
  prod is written to by the deployed pipeline and by migrations only.
- Teammate access: invite via Neon console (org → People) so everyone uses
  their own login; the connection string itself goes only into deploy-time
  env stores.
- **No staging DB** (overview §4) — env-var config means adding one later is
  a Neon branch, which is actually *easier* than the Railway click the plan
  assumed.

---

## 7. CI gates (GitHub Actions, per `testing/TODO.md`)

| Gate | What it runs | Why |
|---|---|---|
| Migration reversibility | `alembic upgrade head` → `alembic downgrade base` → `upgrade head` against a scratch PG 16 service container | Enforces `migrations/TODO.md`'s reversibility rule mechanically; the re-upgrade catches downgrades that "succeed" by dropping too much |
| Schema drift | `alembic check` (autogenerate produces empty diff) | Models and migrations can't silently diverge |
| Seed quality | `seed.py` twice (idempotency) + §2.11 data-quality SQL checks | Duplicate-on-reseed and hollow impact trees are caught before the demo, not during it |

---

## 8. Retention jobs (schema consequences, from data-flows §4)

The daily pipeline cadence runs these deletes; the schema is already shaped
for them (this is why `event_sources.excerpt` is **copied text** with
`raw_document_id SET NULL` — retention can never blank the UI):

| Data | Retention |
|---|---|
| `raw_documents` | 90 days (and truncate stored YouTube transcript bodies to ~20 KB on insert — guide §1.5's storage watch-item) |
| `events` + impacts | 180 days |
| `confident_scores` | latest 30 rows per company |
| `sentiment_pulses` | 90 days |
| `pipeline_runs` | 90 days |
| `refresh_tokens` | expired + 7 days |
| soft-deleted `users` | 30-day grace, then hard delete (CASCADE wipes children) |

---

## 9. Open items to flag at the next team meeting

1. **ADR-008 bucket vote — now urgent.** `consensus.py` on `hong-working` has
   shipped option-2 semantics (Congress/$10B+ → popular_stable, ARK/≤$10B →
   affordable_growing, plus `unresolved`) while the ADR proposes option 1
   (screen-based). The DB doesn't block on this, but the `buckets` stage and
   the homepage copy do. Also: does `unresolved` surface anywhere, or is it
   pipeline-internal? (Schema assumption: internal — `companies.bucket` stays
   NULL for unresolved tickers; the CHECK doesn't need a third value.)
2. **Short interest** is now a real signal — confirm it feeds the Confidence
   Score as evidence (consistent with ADR-008 option 1's "consensus signals
   become score inputs") and confirm the FINRA credentials get provisioned in
   Railway.
3. **NewsAPI vs GNews** (ADR-009) — doesn't change the schema
   (`raw_documents.provider` is free text) but blocks the `news` client.
4. **Role split (§5)** — adopt or defer; 15-minute decision.

---

## Appendix — session log (what was actually done, 2026-08-23)

1. `git fetch origin` + `git pull origin main` → already up to date
   (`origin/main` @ `4821eb7` is an ancestor of `bryan-working` @ `43c505f`;
   the architecture docs commit exists only on `bryan-working` — **merging it
   to `main` is pending team review**).
2. Read: `README.md`, root/database TODOs, `docs/architecture/overview.md`,
   `data-flows.md`, `pipeline-and-schema-guide.md`, ADR-003, ADR-008,
   `schemas/TODO.md`, `migrations/TODO.md`, `seeds/TODO.md`.
3. Inspected sibling branches without checkout (`git show`):
   `hong-working` consensus README + `fmp.py` + `consensus.py` +
   `.env.example`; `cohen-working` file tree + `firestore_upload.py`.
4. Derived the three DDL amendments (§3) and the findings in §1.2 from the
   gap between the 2026-08-03 docs and the current branch code.
5. Wrote this file. No schema code was generated yet — next concrete action is
   Step 0/1 of §4 (docker-compose + Alembic scaffold), which matches build
   plan step 1 in the guide's Part 3.

### Session 2 — Steps 0–1 executed (2026-08-23, same day)

Setup was performed on Bryan's machine; **no migrations were written or run**
(deliberately deferred). What exists now:

1. **Root `.gitignore`** created *before* any `.env` touched disk (`.env`
   ignored, `.env.example` allowed; also `local_data/`, `.venv/`, caches).
   Verified with `git check-ignore`.
2. **`development/docker-compose.yml`** — Postgres 16-alpine, healthcheck,
   named volume. Container up and healthy; server reports PostgreSQL 16.15;
   `citext` and `pg_trgm` both confirmed available in the image.
3. **Host port is 5433, not 5432** — a natively installed `postgresql-x64-17`
   Windows service owns `0.0.0.0:5432` on this machine and silently shadowed
   the container (host connections authenticated against the *wrong* server).
   Moving the container to 5433 avoids fighting a service other software may
   depend on, and costs teammates nothing.
4. **`development/backend/.env.example`** — extended `hong-working`'s version
   with the FINRA vars (§1.2 finding #3), `ANTHROPIC_API_KEY`, and the working
   local `DATABASE_URL`. Local `.env` created (untracked).
5. **Alembic scaffold** (`alembic.ini`, `migrations/env.py`,
   `script.py.mako`, empty `versions/`): filename template matches
   `migrations/TODO.md`'s `YYYYMMDDHHMMSS_description` convention;
   `env.py` reads `DATABASE_URL` from the environment (loads `.env` via
   python-dotenv), `compare_type` + `compare_server_default` on.
6. **`src/models/base.py`** — `DeclarativeBase` with the constraint
   **naming convention** (§4 Step 1's non-negotiable; reversibility depends
   on deterministic constraint names). No model classes yet.
7. **Tooling**: `.venv` (Python 3.11) with pinned `requirements-db.txt`
   (SQLAlchemy 2.0.52, Alembic 1.19.1, psycopg 3.3.4, python-dotenv;
   `tzdata` on Windows for Alembic's `timezone = utc`).
8. **Dev commands**: `development/Makefile` (Mac/Linux) and
   `development/db.ps1` (Windows) with the same verbs:
   up / down / upgrade / downgrade / current / psql / reset.
9. **Verified end-to-end**: `alembic current` and a raw SQLAlchemy
   connection both reach the containerized PG 16.15 as `perennial` on
   `localhost:5433`. `alembic heads` is empty — zero revisions exist, as
   intended.

**Next action:** migration 001 (§4 Step 2 — extensions + Tiers 0/2/3/5 with
the §3 amendments), then the CI reversibility gate (§7).

### Session 3 — migration 001 + CI gate (2026-08-23/24)

1. **Migration 001 exists and is tested**:
   `migrations/versions/20260824034321_initial_content_schema.py` — extensions
   (citext, pg_trgm) + all of Tiers 0/2/3/5, with the §3 amendments applied
   (`short_interest` in the signal_type CHECK, `events.published` from day
   one). Every constraint is explicitly named (pk_/uq_/ck_/fk_) so future
   migrations can drop them by name. Hand-written rather than autogenerated —
   the CHECK constraints, partial indexes, and the trigram GIN index are
   exactly what autogenerate misses.
2. **Reversibility verified locally**: `upgrade head` → `downgrade base` →
   `upgrade head`, all clean. Constraint spot-check: an INSERT with
   `traffic_light='purple'` is rejected by `ck_companies_traffic_light`.
3. **CI gate added**: `.github/workflows/db-ci.yml` runs the same
   up→down→re-up cycle against a scratch PG 16 container on every PR touching
   `development/backend/`.
4. **`migrations/env.py` now normalizes the URL scheme** — Railway/Heroku
   hand out `postgres://`/`postgresql://`; either is rewritten to
   `postgresql+psycopg://` automatically.
5. **Autogenerate warning**: model classes don't exist yet (only `Base`).
   Until models catch up with the tables, `alembic revision --autogenerate`
   would propose dropping everything — write migrations by hand, and don't
   add `alembic check` to CI until models exist.

**Production note (per team decision to build prod-first):** provision the
Railway Postgres (§6), then run `alembic upgrade head` with `DATABASE_URL`
pointing at it — as a deploy/release step, never on app startup.

**Next action:** SQLAlchemy models for the created tables, then the
fetcher-to-Postgres swap (start with `ark.py` — no API key required).

### Session 4 — production database provisioned on Neon (2026-08-24)

1. **Railway attempted first** (CLI installed, Bryan authenticated) —
   project creation failed: *"Free plan resource provision limit exceeded."*
   Team decision: **Neon free tier** for the DB now; compute platform
   deferred until the API exists (options table discussed: Neon / Supabase /
   Render / GitHub Student Pack credits).
2. **Neon provisioned via CLI** (`neonctl`): project `perennial`, explicitly
   pinned `--pg-version 16` for local/prod parity → got 16.15, matching the
   local container exactly.
3. **Migration 001 applied to prod** (`alembic upgrade head` with
   `DATABASE_URL` pointed at Neon) and verified with `check_db.py`
   (new read-only script in `development/backend/`): 9 tables +
   `alembic_version` at `e12d2abbc333`, `citext` + `pg_trgm` installed.
4. §6 above rewritten from the Railway plan to the Neon reality.
   overview.md §4's topology diagram still says Railway — flag for the next
   docs pass rather than rewriting the architecture docs unilaterally.

**Next actions unchanged** (models → fetcher swap), plus: invite teammates
in the Neon console, and claim the GitHub Student Developer Pack before
committing to a compute platform.
