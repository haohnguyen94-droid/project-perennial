# Perennial — Database & Pipeline Implementation Guide

**Owner:** @bryan (pipelines + database) · **Date:** 2026-08-03
**Depends on:** [overview.md](overview.md) (components), [data-flows.md](data-flows.md) (workflows), [ADR-003](decisions/ADR-003-postgres-single-store.md) (Postgres), [ADR-004](decisions/ADR-004-hourly-batch-pipeline.md) (cadence), [ADR-005](decisions/ADR-005-claude-sonnet-ingest-only.md) (LLM), [ADR-008](decisions/ADR-008-bucket-semantics.md) (buckets — **still needs a vote**)

This is the build-from document. Part 1 is the database (DDL, relationships, joins, indexes). Part 2 is the pipeline (module layout, stage contract, idempotency, budgets, errors, testing). Part 3 is the order to build it in.

Three schema decisions here **supersede** the first-pass sketch in data-flows.md; each is flagged 🔧 with the reason.

---

# PART 1 — DATABASE

## 1.1 Design rules (apply these everywhere)

| Rule | Why |
|---|---|
| `uuid` primary keys, `gen_random_uuid()` default | Repo convention (`database/schemas/TODO.md`); built into PG 13+, no extension |
| `timestamptz` for every instant, **UTC everywhere** | `timestamp` without zone is a bug factory across a distributed team; the pipeline reasons in UTC |
| Explicit `date` columns for daily-uniqueness, never `captured_at::date` | 🔧 Casting a `timestamptz` to `date` depends on the session `TimeZone` setting, so an expression-based unique index is **not stable**. Store `as_of_date date` and set it explicitly in the pipeline |
| `text` + `CHECK (col IN (...))` for enums, not PG `ENUM` types | Adding/renaming a value in a PG enum type is an awkward migration; a CHECK constraint is a one-line `ALTER`. Alembic handles it cleanly |
| `numeric` for all money and ratios, **never `float`** | Binary floats can't represent `0.1`; prices and percentages must round-trip exactly |
| `jsonb` only for data you *display*, never for data you *filter or join on* | `breakdown`, `top_excerpts`, `payload` are read-and-render. The moment you want `WHERE payload->>'x' = …` in a hot path, that field wants to be a column |
| Every FK gets an index | Postgres does **not** auto-index the referencing side; unindexed FKs make cascade deletes and joins scan |
| `ON DELETE CASCADE` on user-owned rows; `RESTRICT` on reference data | Deleting a user should erase their rows (Workflow 6). Deleting a sector out from under companies should fail loudly |

**Honest scale note:** at 50–150 companies and <100 users, Postgres will seq-scan most of these tables in under a millisecond and be right to. The indexes below are not (mostly) performance necessities — they are *correctness of intent* plus insurance for the tables that do grow (`raw_documents`, `confident_scores`, `sentiment_pulses`). Don't add more than this list without a measurement.

## 1.2 Full DDL, in migration order

Dependency order matters — this is the order Alembic must create them.

```sql
CREATE EXTENSION IF NOT EXISTS citext;      -- case-insensitive email

-- ══════════════════════════════════════════════════════════
-- TIER 0 — reference data (pipeline-written, rarely changes)
-- ══════════════════════════════════════════════════════════

CREATE TABLE sectors (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name          text NOT NULL UNIQUE,            -- canonical slug: 'tech', 'energy'
  display_label text NOT NULL,                   -- beginner-facing: 'Tech'
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE companies (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker        text NOT NULL UNIQUE,            -- natural key the fetchers speak
  name          text NOT NULL,
  sector_id     uuid NOT NULL REFERENCES sectors(id) ON DELETE RESTRICT,
  market_cap    numeric(24,2),
  current_price numeric(18,4),
  traffic_light text CHECK (traffic_light IN ('green','yellow','red')),
  momentum      text CHECK (momentum IN ('up','down','flat')),

  -- bucket membership + WHY it's a member (explainability invariant)
  bucket             text CHECK (bucket IN ('affordable_growing','popular_stable')),
  bucket_explanation text,

  is_active     boolean NOT NULL DEFAULT true,   -- the 50–150 ticker universe (Q7)

  -- rolling-refresh watermarks (see §2.6 budget math)
  quote_refreshed_at        timestamptz,
  fundamentals_refreshed_at timestamptz,

  last_updated  timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX companies_sector_idx  ON companies (sector_id);
CREATE INDEX companies_bucket_idx  ON companies (bucket) WHERE is_active;
CREATE INDEX companies_search_idx  ON companies USING gin (
  (ticker || ' ' || name) gin_trgm_ops);        -- needs: CREATE EXTENSION pg_trgm;

-- ══════════════════════════════════════════════════════════
-- TIER 1 — users & auth (API-written ONLY)
-- ══════════════════════════════════════════════════════════

CREATE TABLE users (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email                citext NOT NULL UNIQUE,
  password_hash        text NOT NULL,
  name                 text,
  investment_summary   text,                     -- Profile screen "Investment" field
  onboarding_completed boolean NOT NULL DEFAULT false,
  deleted_at           timestamptz,              -- soft delete, 30-day grace
  created_at           timestamptz NOT NULL DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX users_pending_deletion_idx ON users (deleted_at)
  WHERE deleted_at IS NOT NULL;                  -- the retention sweep's only scan

CREATE TABLE refresh_tokens (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash text NOT NULL UNIQUE,               -- store the HASH, never the token
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX refresh_tokens_user_idx ON refresh_tokens (user_id);

CREATE TABLE user_interests (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id        uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  interest_type  text NOT NULL CHECK (interest_type IN ('sector','theme')),
  interest_value text NOT NULL,                  -- matches sectors.name when type='sector'
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, interest_type, interest_value)   -- ← makes onboarding save idempotent
);
CREATE INDEX user_interests_user_idx ON user_interests (user_id);

CREATE TABLE user_notification_preferences (
  user_id       uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  channels      jsonb NOT NULL DEFAULT '{}'::jsonb,
  frequency     text,
  types_enabled jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at    timestamptz NOT NULL DEFAULT now()
);

-- 🔧 SUPERSEDES data-flows.md: two nullable FKs + XOR check, not (target_type, target_id).
--    Polymorphic target_id cannot have a foreign key, so a deleted company would leave
--    dangling watchlist rows that the enrichment join silently drops. This shape gets
--    real referential integrity and free cascades. The API contract is unchanged:
--    ?filter=companies → WHERE company_id IS NOT NULL.
CREATE TABLE watchlist_items (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_id    uuid REFERENCES companies(id) ON DELETE CASCADE,
  sector_id     uuid REFERENCES sectors(id)   ON DELETE CASCADE,
  has_new_event boolean NOT NULL DEFAULT false,  -- pipeline sets, API clears
  added_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT watchlist_exactly_one_target CHECK (
    (company_id IS NOT NULL AND sector_id IS NULL) OR
    (company_id IS NULL AND sector_id IS NOT NULL))
);
CREATE UNIQUE INDEX watchlist_company_uniq ON watchlist_items (user_id, company_id)
  WHERE company_id IS NOT NULL;                  -- ← makes "add" idempotent
CREATE UNIQUE INDEX watchlist_sector_uniq  ON watchlist_items (user_id, sector_id)
  WHERE sector_id IS NOT NULL;
CREATE INDEX watchlist_user_idx ON watchlist_items (user_id);

-- ══════════════════════════════════════════════════════════
-- TIER 2 — operations ledger (pipeline-written)
-- ══════════════════════════════════════════════════════════

CREATE TABLE pipeline_runs (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  trigger     text NOT NULL CHECK (trigger IN ('cron','manual')),
  cadence     text NOT NULL CHECK (cadence IN ('hourly','daily')),
  status      text NOT NULL CHECK (status IN ('running','succeeded','partial','failed')),
  started_at  timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz,
  stages      jsonb NOT NULL DEFAULT '{}'::jsonb
    -- {"news": {"status":"ok","written":12,"skipped":3,"ms":4210,"error":null}, ...}
);
CREATE INDEX pipeline_runs_recent_idx ON pipeline_runs (started_at DESC);

-- ══════════════════════════════════════════════════════════
-- TIER 3 — ingestion staging (pipeline-written, pipeline-read only)
-- ══════════════════════════════════════════════════════════

CREATE TABLE raw_documents (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type  text NOT NULL CHECK (source_type IN ('news','social_media','analyst')),
  provider     text NOT NULL,                    -- 'newsapi' | 'youtube' | 'finnhub'
  external_id  text NOT NULL,                    -- url-hash | video-id | provider id
  title        text,
  body         text,
  url          text,
  author       text,
  published_at timestamptz,
  payload      jsonb NOT NULL DEFAULT '{}'::jsonb,  -- view counts, tags, channel…
  fetched_at   timestamptz NOT NULL DEFAULT now(),
  processed_at timestamptz,                      -- ← the watermark. NULL = new work
  UNIQUE (provider, external_id)                 -- ← refetch is a no-op
);
CREATE INDEX raw_documents_unprocessed_idx
  ON raw_documents (source_type, published_at DESC) WHERE processed_at IS NULL;

CREATE TABLE consensus_signals (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  ticker      text NOT NULL,                     -- fetchers see tickers outside our universe
  company_id  uuid REFERENCES companies(id) ON DELETE CASCADE,  -- NULL if off-universe
  signal_type text NOT NULL CHECK (signal_type IN
                ('congress_trade','ark_holding','insider_buy')),
  dedupe_key  text NOT NULL,                     -- computed in Python, see §2.5
  payload     jsonb NOT NULL,                    -- the dicts fmp.py/ark.py/insider.py emit
  observed_at date NOT NULL,
  fetched_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (signal_type, dedupe_key)
);
CREATE INDEX consensus_company_idx ON consensus_signals (company_id, signal_type, observed_at DESC);

-- ══════════════════════════════════════════════════════════
-- TIER 4 — market time series (pipeline-written)
-- ══════════════════════════════════════════════════════════

-- 🔧 SUPERSEDES data-flows.md: explicit as_of_date, not captured_at::date (see §1.1)
CREATE TABLE company_price_snapshots (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id    uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  as_of_date    date NOT NULL,
  captured_at   timestamptz NOT NULL DEFAULT now(),
  price         numeric(18,4),
  week_52_low   numeric(18,4),
  week_52_high  numeric(18,4),
  week_52_avg   numeric(18,4),
  fair_value_low  numeric(18,4),
  fair_value_high numeric(18,4),
  UNIQUE (company_id, as_of_date)                -- one row/day → re-run safe
);
CREATE INDEX price_snapshots_latest_idx ON company_price_snapshots (company_id, as_of_date DESC);

CREATE TABLE company_financials (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  year       smallint NOT NULL,
  revenue    numeric(24,2),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (company_id, year)                      -- 5-yr RevenueChart
);

-- ══════════════════════════════════════════════════════════
-- TIER 5 — insight content (pipeline-written; ✦ = LLM-generated)
-- ══════════════════════════════════════════════════════════

CREATE TABLE events (
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  slug                    text UNIQUE,
  headline                text NOT NULL,
  summary                 text,
  what_happened           text,                  -- ✦
  effects_markets_summary text,                  -- ✦
  impact_level            text CHECK (impact_level IN ('high','medium','low')),
  source_name             text,
  source_url              text,
  published_at            timestamptz NOT NULL,
  content_hash            text NOT NULL UNIQUE,  -- ← LLM regeneration gate (§2.7)
  pipeline_run_id         uuid REFERENCES pipeline_runs(id) ON DELETE SET NULL,
  created_at              timestamptz NOT NULL DEFAULT now(),
  updated_at              timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX events_recent_idx ON events (published_at DESC);

CREATE TABLE event_sector_impacts (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id    uuid NOT NULL REFERENCES events(id)  ON DELETE CASCADE,
  sector_id   uuid NOT NULL REFERENCES sectors(id) ON DELETE CASCADE,
  impact_type text NOT NULL CHECK (impact_type IN ('positive','negative','neutral')),
  explanation text NOT NULL,                     -- ✦ never null: the flow node's "why"
  UNIQUE (event_id, sector_id)
);
CREATE INDEX esi_sector_idx ON event_sector_impacts (sector_id);

CREATE TABLE event_company_impacts (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id      uuid NOT NULL REFERENCES events(id)    ON DELETE CASCADE,
  company_id    uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  via_sector_id uuid REFERENCES sectors(id) ON DELETE SET NULL,  -- which branch it hangs off
  impact_type   text NOT NULL CHECK (impact_type IN ('positive','negative','neutral')),
  explanation   text NOT NULL,                   -- ✦
  UNIQUE (event_id, company_id)                  -- ← one node per company per event
);
CREATE INDEX eci_company_idx ON event_company_impacts (company_id);
CREATE INDEX eci_event_sector_idx ON event_company_impacts (event_id, via_sector_id);

CREATE TABLE event_sources (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_id        uuid NOT NULL REFERENCES events(id) ON DELETE CASCADE,
  raw_document_id uuid REFERENCES raw_documents(id) ON DELETE SET NULL,  -- survives retention
  source_type     text NOT NULL CHECK (source_type IN ('news','social_media','analyst')),
  excerpt         text NOT NULL,                 -- copied, so retention can't blank the UI
  url             text,
  sentiment       text CHECK (sentiment IN ('positive','mixed','negative'))
);
CREATE INDEX event_sources_event_idx ON event_sources (event_id, source_type);

-- ══════════════════════════════════════════════════════════
-- TIER 6 — scoring & sentiment (pipeline-written)
-- ══════════════════════════════════════════════════════════

CREATE TABLE confident_scores (                  -- append-only history
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id              uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  score                   smallint NOT NULL CHECK (score BETWEEN 0 AND 100),
  breakdown               jsonb NOT NULL,        -- ✦ [{factor,weight,contribution,explanation}]
  event_exposure_summary  text,                  -- ✦
  analyst_outlook_summary text,                  -- ✦
  inputs_hash             text NOT NULL,         -- ← LLM text regeneration gate (§2.7)
  captured_at             timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX scores_latest_idx ON confident_scores (company_id, captured_at DESC);  -- ★ hot

CREATE TABLE sentiment_pulses (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id   uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  source_type  text NOT NULL CHECK (source_type IN ('news','social_media','analyst')),
  as_of_date   date NOT NULL,                    -- 🔧 explicit, see §1.1
  positive_pct smallint NOT NULL CHECK (positive_pct BETWEEN 0 AND 100),
  mixed_pct    smallint NOT NULL CHECK (mixed_pct    BETWEEN 0 AND 100),
  negative_pct smallint NOT NULL CHECK (negative_pct BETWEEN 0 AND 100),
  top_excerpts jsonb NOT NULL DEFAULT '[]'::jsonb,   -- [{excerpt,url,sentiment}]
  sample_size  integer NOT NULL DEFAULT 0,       -- honesty: "based on 3 articles"
  captured_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (company_id, source_type, as_of_date),
  CONSTRAINT pulse_pcts_sum CHECK (positive_pct + mixed_pct + negative_pct = 100)
);
CREATE INDEX pulses_latest_idx ON sentiment_pulses (company_id, source_type, as_of_date DESC);

CREATE TABLE why_this_company (
  company_id   uuid PRIMARY KEY REFERENCES companies(id) ON DELETE CASCADE,
  key_reasons  jsonb NOT NULL,                   -- ✦ [{reason, explanation}]
  inputs_hash  text NOT NULL,
  last_updated timestamptz NOT NULL DEFAULT now()
);
```

**On `updated_at`:** set it in SQLAlchemy (`onupdate=func.now()`) rather than with triggers — one place to look, and it survives being read by a teammate who doesn't know the trigger exists.

## 1.3 Relationship inventory

| Parent | Child | Card. | Delete rule | Note |
|---|---|---|---|---|
| sectors | companies | 1→N | RESTRICT | Every company has exactly one sector |
| companies | company_price_snapshots | 1→N | CASCADE | One row/day |
| companies | company_financials | 1→N | CASCADE | One row/year |
| companies | confident_scores | 1→N | CASCADE | Append-only; read latest |
| companies | sentiment_pulses | 1→N | CASCADE | 3 source types × day |
| companies | why_this_company | 1→**1** | CASCADE | Current state only, no history |
| events | event_sector_impacts | 1→N | CASCADE | Tier 1 of the flow tree |
| events | event_company_impacts | 1→N | CASCADE | Tier 2 (via `via_sector_id`) |
| events | event_sources | 1→N | CASCADE | News/social/analyst citations |
| sectors ← event_sector_impacts → events | | **N↔M** | CASCADE | Join table *with payload* (impact + explanation) — that payload is why it can't be a bare link table |
| companies ← event_company_impacts → events | | **N↔M** | CASCADE | Same |
| users | user_interests / prefs / watchlist / refresh_tokens | 1→N (prefs 1→1) | CASCADE | Account deletion is one `DELETE FROM users` |
| companies/sectors | watchlist_items | 1→N | CASCADE | XOR-constrained (§1.2) |
| raw_documents | event_sources | 1→N | SET NULL | Excerpt text is copied, so 90-day retention can't blank the UI |

**The tree shape to hold in your head:** `events → event_sector_impacts → (event_company_impacts filtered by via_sector_id)`. That two-level fan-out *is* the Event Impact Flow. Everything else in Tier 5–6 hangs off `companies`.

## 1.4 The five queries that matter

Four of the five need "the latest row per company." **`LEFT JOIN LATERAL … LIMIT 1` is the idiom** — it filters the outer set first, then does one index seek per surviving row, and it degrades gracefully to `NULL` when a company has no score yet (which `DISTINCT ON` won't do without a second pass). Learn this one pattern and four of the five queries write themselves.

**Q1 — Homepage bucket list** (`GET /api/homepage`)

```sql
SELECT c.id, c.ticker, c.name, c.current_price, c.traffic_light, c.momentum,
       s.display_label AS sector, cs.score, cs.captured_at AS score_as_of
FROM companies c
JOIN sectors s ON s.id = c.sector_id
LEFT JOIN LATERAL (
    SELECT score, captured_at FROM confident_scores
    WHERE company_id = c.id ORDER BY captured_at DESC LIMIT 1
) cs ON true
WHERE c.is_active AND c.bucket = :bucket          -- 'affordable_growing' | 'popular_stable'
ORDER BY cs.score DESC NULLS LAST, c.ticker
LIMIT 20;
```
Served by `companies_bucket_idx` + `scores_latest_idx`. Run once per bucket.

**Q2 — Personalized Insight feed** (same endpoint). Ranks by interest overlap, then impact, then recency — and **falls back to global recency when the user has no matches**, so a new user's homepage is never empty:

```sql
SELECT e.id, e.headline, e.summary, e.impact_level, e.published_at,
       count(ui.id) AS interest_hits
FROM events e
JOIN event_sector_impacts esi ON esi.event_id = e.id
JOIN sectors s ON s.id = esi.sector_id
LEFT JOIN user_interests ui
       ON ui.user_id = :user_id
      AND ui.interest_type = 'sector'
      AND ui.interest_value = s.name
WHERE e.published_at > now() - interval '7 days'
GROUP BY e.id
ORDER BY interest_hits DESC,
         CASE e.impact_level WHEN 'high' THEN 3 WHEN 'medium' THEN 2 ELSE 1 END DESC,
         e.published_at DESC
LIMIT 10;
```

**Q3 — Event detail with the nested impact tree** (`GET /api/events/:id`). One round trip, shaped exactly as `EventImpactFlow` consumes it:

```sql
SELECT e.id, e.headline, e.what_happened, e.effects_markets_summary, e.impact_level,
  (SELECT json_agg(json_build_object(
      'sector',      s.display_label,
      'impact',      esi.impact_type,
      'explanation', esi.explanation,
      'companies',   COALESCE((
          SELECT json_agg(json_build_object(
                   'company_id',  c.id,     'ticker', c.ticker,
                   'name',        c.name,   'impact', eci.impact_type,
                   'explanation', eci.explanation))
          FROM event_company_impacts eci
          JOIN companies c ON c.id = eci.company_id
          WHERE eci.event_id = e.id AND eci.via_sector_id = esi.sector_id
      ), '[]'::json)))
   FROM event_sector_impacts esi
   JOIN sectors s ON s.id = esi.sector_id
   WHERE esi.event_id = e.id) AS impact_tree
FROM events e
WHERE e.id = :event_id;
```

> **Start with three plain queries assembled in Python instead**, and only adopt this once the shape is settled. The `json_agg` version is genuinely faster and gives the frontend its tree for free, but it is materially harder to debug when the LLM writes something odd — and in month one, it will. This is a refactor to reach for later, not a starting point.

**Q4 — Watchlist with enrichment** (`GET /api/user/watchlist?filter=`). The XOR design (§1.2) makes this two clean LEFT JOINs:

```sql
SELECT w.id, w.has_new_event, w.added_at,
       c.id AS company_id, c.ticker, c.name AS company_name, c.current_price,
       sec.display_label AS sector_name,
       cs.score,
       sp.positive_pct, sp.mixed_pct, sp.negative_pct
FROM watchlist_items w
LEFT JOIN companies c   ON c.id   = w.company_id
LEFT JOIN sectors   sec ON sec.id = COALESCE(w.sector_id, c.sector_id)
LEFT JOIN LATERAL (
    SELECT score FROM confident_scores
    WHERE company_id = w.company_id ORDER BY captured_at DESC LIMIT 1
) cs ON w.company_id IS NOT NULL
LEFT JOIN LATERAL (
    SELECT positive_pct, mixed_pct, negative_pct FROM sentiment_pulses
    WHERE company_id = w.company_id AND source_type = 'news'
    ORDER BY as_of_date DESC LIMIT 1
) sp ON w.company_id IS NOT NULL
WHERE w.user_id = :user_id
  AND (:filter = 'all'
       OR (:filter = 'companies' AND w.company_id IS NOT NULL)
       OR (:filter = 'sectors'   AND w.sector_id  IS NOT NULL))
ORDER BY w.added_at DESC;
```

**Q5 — Company detail bundle** (`GET /api/companies/:id`). Five small queries in one service function, not one monster join — a company's 3 sentiment rows, 5 financial rows, and N event impacts are independent result *sets*, and forcing them into one query gives you a cross-product to de-duplicate in Python. Explicitly:

1. company + sector + latest score/breakdown (LATERAL, as Q1)
2. latest `company_price_snapshots` row → PriceOverview + WeekRangeBar
3. `sentiment_pulses` latest per source → `DISTINCT ON (source_type)` ordered by `source_type, as_of_date DESC`
4. `company_financials ORDER BY year` → RevenueChart
5. recent `event_company_impacts ⋈ events` (limit 5) → Event Exposure

Then assemble the Pydantic response. Five indexed lookups is ~1 ms total here; readability wins.

## 1.5 Storage watch-item

`raw_documents.body` holds full YouTube transcripts — roughly 40–80 KB each. At ~50 videos/day over the 90-day retention that's a few hundred MB, which is fine on Railway's starter tier but is *the* table that will surprise you. Two mitigations, in order of preference: truncate stored bodies to the first ~20 KB (sentiment classification never needs more), and let the 90-day retention job actually run from day one rather than "when we get to it."

---

# PART 2 — PIPELINE

## 2.1 Module layout

```
backend/pipeline/
  run.py              # CLI entrypoint + orchestrator
  context.py          # RunContext: session factory, run_id, budgets, logger, clock
  registry.py         # stage registry, cadence filter, topological ordering
  stages/
    market_data.py    consensus.py    news.py       social.py
    events.py ✦       impact_flow.py ✦ sentiment.py  scoring.py
    buckets.py        retention.py
  clients/
    base.py           # BudgetedClient: budget + retry + structured logging
    fmp.py  finnhub.py  newsapi.py  ark.py  securitiesdb.py  youtube.py
  llm/
    client.py         # Anthropic wrapper (structured outputs, batching)
    schemas.py        # Pydantic models the LLM must fill
    prompts/          # versioned .md prompt templates
```

Stages never import each other. They communicate **only through tables** — that's what makes each one independently re-runnable, which is what makes "the next hourly run is the retry" a safe policy rather than a hope.

## 2.2 The stage contract

```python
class StageResult(NamedTuple):
    written: int
    skipped: int
    notes: dict[str, Any]

class Stage(Protocol):
    name: str
    cadence: Literal["hourly", "daily"]
    depends_on: tuple[str, ...]
    def run(self, ctx: RunContext) -> StageResult: ...
```

Every stage obeys four rules:

1. **Idempotent.** Running it twice changes nothing the second time (§2.5).
2. **Bounded.** It reads its own watermark and processes only new work.
3. **Self-reporting.** It returns counts; the orchestrator writes them to `pipeline_runs.stages`.
4. **Network first, then write.** Do all HTTP into memory, then open one short transaction and write. Never hold a DB transaction open across an external call — a slow provider shouldn't hold row locks for 30 seconds.

## 2.3 Orchestrator

```python
def main(cadence: str, only: list[str] | None):
    with advisory_lock() as acquired:          # see below
        if not acquired:
            log.warning("run already in progress; exiting"); return
        run_id = insert_pipeline_run(cadence, status="running")
        stages = registry.select(cadence, only)         # topologically ordered
        results, failed = {}, set()
        for stage in stages:
            if failed & set(stage.depends_on):
                results[stage.name] = {"status": "skipped_dep"}; continue
            try:
                r = stage.run(ctx)
                results[stage.name] = {"status": "ok", **r._asdict()}
            except StageFailed as e:                     # budget exhausted, provider down
                failed.add(stage.name)
                results[stage.name] = {"status": "failed", "error": str(e)}
                log.exception("stage failed", stage=stage.name)
        finish_run(run_id, results)   # 'succeeded' | 'partial' | 'failed'
```

**Concurrency guard — use a Postgres advisory lock, not a status-row check.** A `SELECT … WHERE status='running'` check has a race between read and write and leaves a permanent lock if a run crashes mid-flight. An advisory lock is held by the session and released automatically when the connection dies:

```python
@contextmanager
def advisory_lock(key: int = 8_675_309):
    conn = engine.connect()
    got = conn.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": key}).scalar()
    try:
        yield got
    finally:
        if got:
            conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": key})
        conn.close()
```

## 2.4 Stage-by-stage

| Stage | Cadence | Depends on | Reads | Writes | Watermark |
|---|---|---|---|---|---|
| `market_data` | hourly (quotes) / daily (fundamentals) | — | FMP | `companies`, `company_price_snapshots`, `company_financials` | `quote_refreshed_at`, `fundamentals_refreshed_at` |
| `news` | hourly | — | News API | `raw_documents` | `(provider, external_id)` conflict |
| `social` | daily | — | YouTube + yt-dlp | `raw_documents` | same |
| `consensus` | daily | — | FMP/ARK/SecuritiesDB | `consensus_signals` | `(signal_type, dedupe_key)` |
| `events` ✦ | hourly | news | `raw_documents WHERE processed_at IS NULL` | `events`, `event_sources` | `content_hash` |
| `impact_flow` ✦ | hourly | events | events lacking impacts | `event_sector_impacts`, `event_company_impacts` | existence of impact rows |
| `sentiment` | hourly | news, social, consensus | unprocessed docs + Finnhub | `sentiment_pulses`; stamps `processed_at` | `(company, source, as_of_date)` |
| `scoring` ✦ | hourly | market_data, sentiment, impact_flow | current state | `confident_scores`, `why_this_company` | `inputs_hash` |
| `buckets` | hourly | scoring | companies + criteria | `companies.bucket`, `watchlist_items.has_new_event` | idempotent overwrite |
| `retention` | daily | — | dates | deletes | idempotent |

## 2.5 Idempotency — the concrete pattern

Every write is an upsert on a natural key. In SQLAlchemy:

```python
from sqlalchemy.dialects.postgresql import insert

stmt = insert(RawDocument).values(rows)
stmt = stmt.on_conflict_do_update(
    index_elements=["provider", "external_id"],
    set_={"title": stmt.excluded.title, "body": stmt.excluded.body,
          "payload": stmt.excluded.payload, "fetched_at": func.now()},
)
session.execute(stmt)
```

Natural keys by table: `raw_documents(provider, external_id)` · `consensus_signals(signal_type, dedupe_key)` · `events(content_hash)` · `company_price_snapshots(company_id, as_of_date)` · `sentiment_pulses(company_id, source_type, as_of_date)` · `company_financials(company_id, year)` · `event_*_impacts(event_id, …)` · `why_this_company(company_id)`.

**`dedupe_key` for consensus signals** — build it in Python from the fields that identify a real-world transaction, mirroring what `fmp.py`'s `deduplicate()` already computes:

```python
dedupe_key = hashlib.sha256("|".join([
    politician_name.lower(), ticker, transaction_date, trade_type.lower()
]).encode()).hexdigest()
```
That lets FMP and Senate Stock Watcher both report the same trade without creating two rows — which is exactly the collision Hao's existing code already handles in memory. Moving it to a DB constraint means it survives across runs, not just within one.

**`confident_scores` is the deliberate exception** — it appends a new row every run by design (it's the score history). Its "idempotency" is that re-running produces the same *score* from the same inputs; `inputs_hash` prevents the expensive part (LLM text) from being redone.

## 2.6 Budget enforcement — and the FMP math that forces a design choice

Every client wraps a budget. Exhaustion raises `BudgetExhausted(StageFailed)` → that stage goes `failed`, the run goes `partial`, independent stages continue.

```python
class BudgetedClient:
    def __init__(self, name, daily_limit, session):
        self.name, self.limit = name, daily_limit
        self.used = load_today_usage(session, name)

    @retry(retry=retry_if_exception_type(TransientError),
           wait=wait_exponential(1, 30), stop=stop_after_attempt(3))
    def get(self, path, **params):
        if self.used >= self.limit:
            raise BudgetExhausted(f"{self.name}: {self.used}/{self.limit}")
        self.used += 1
        ...  # httpx call; 429/5xx → TransientError; 4xx → PermanentError
```

**The FMP constraint is real and it shapes the schedule.** Free tier is 250 requests/day (documented in the header of `fmp.py` on `origin/hong-working`). A naive plan blows it:

| Job | Naive | Cost/day | Fix | Cost/day |
|---|---|---|---|---|
| Hourly quotes, 150 tickers | 150 calls × 24 | 3,600 ❌ | **Batch** the symbol list (~50/call) → 3 calls × 24 | 72 |
| Daily fundamentals, 150 tickers | 150 calls | 150 ⚠️ | **Rolling refresh**: 25 stalest tickers/day, full cycle every 6 days | 25 |
| Congress trades | 3 pages × 2 chambers | 6 | unchanged | 6 |
| | | **3,756** | | **~103** ✅ |

Rolling refresh is the interesting one and it generalizes: **refresh cadence should match how fast the data actually changes.** Revenue history updates quarterly, so a 6-day refresh cycle is 15× more current than the data itself. Implement it with `ORDER BY fundamentals_refreshed_at NULLS FIRST LIMIT 25`.

## 2.7 The LLM stages

Two gates keep cost bounded and quality checkable (per [ADR-005](decisions/ADR-005-claude-sonnet-ingest-only.md)):

**Hash gate.** `content_hash = sha256(sorted(raw_document_ids) + prompt_version)`. Same inputs *and* same prompt version → the event already exists → no call. Including the prompt version in the hash means editing a prompt correctly forces regeneration, which you want.

**Universe gate.** The prompt is handed the exact sector list and active tickers; the response is parsed with `client.messages.parse` against a Pydantic schema; then **every returned ticker and sector is checked against the DB before insert**, and anything unrecognized is dropped and counted in `StageResult.notes`. This is your hallucination floor — a model naming a plausible-but-nonexistent ticker can never reach a user.

```python
class CompanyImpact(BaseModel):
    ticker: str
    impact: Literal["positive", "negative", "neutral"]
    explanation: str = Field(min_length=20, max_length=280)

class SectorImpact(BaseModel):
    sector: str
    impact: Literal["positive", "negative", "neutral"]
    explanation: str = Field(min_length=20, max_length=280)
    companies: list[CompanyImpact]

class ImpactFlow(BaseModel):
    sectors: list[SectorImpact] = Field(min_length=1, max_length=4)
```

`min_length` on explanations enforces the repo's own rule that every number ships with a real "why" rather than a two-word stub; `max_length` keeps it renderable in the flow node. Track `notes["dropped_tickers"]` — a rising count is your early-warning signal for prompt drift.

## 2.8 Errors

| Class | Examples | Handling |
|---|---|---|
| `TransientError` | 429, 5xx, timeout, connection reset | tenacity retry, exponential backoff, honor `Retry-After` |
| `SkipItem` | one malformed record, missing ticker, unparseable date | log + `skipped += 1`, continue the loop |
| `StageFailed` | budget exhausted, auth failure, provider fully down | abort *this* stage, mark it failed, run continues |

The rule underneath: **one bad record must never cost you the batch.** Hao's parsers already work this way (`try/except` per record with a counter) — keep that discipline in every stage you write.

## 2.9 Testing

- **No network in unit tests.** Each client gets a `Fake*Client` reading `tests/fixtures/*.json` — record real responses once, commit them.
- **Idempotency test per stage** (the highest-value test you will write): run the stage twice against a seeded DB, assert row counts identical and no duplicate-key errors.
- **LLM stages** unit-test against recorded responses; quality is tested separately by the eval harness (build-plan.md §0), which is a different kind of test and should live in `testing/` with its own runner.
- **Migration test in CI:** `alembic upgrade head` then `downgrade base` on a scratch DB — enforces the reversibility rule from `database/migrations/TODO.md`.

## 2.10 CLI

```bash
python -m pipeline.run --cadence hourly
python -m pipeline.run --cadence daily
python -m pipeline.run --stage news,events,impact_flow   # partial re-run
python -m pipeline.run --stage impact_flow --dry-run     # no writes, log intent
python -m pipeline.run --stage events --force            # bypass hash gate
```

`--dry-run` and `--force` will save you hours while tuning prompts. Build them in week one, not when you finally need them.

## 2.11 Data quality gates

§2.9 covers **code** quality (tests, CI, migration reversibility). This section covers **data** quality: assertions about the rows the pipeline just produced. These are different failure modes — the code can be green while the pipeline quietly publishes an event whose impact tree has no companies in it.

You do not need Great Expectations, Soda, or dbt tests for this. You need one `validate` stage and about fifteen SQL assertions.

### The checks

Three tiers, by what they catch.

**Tier 1 — invariants (already enforced by CHECK constraints, listed for completeness).** Score in 0–100; sentiment percentages sum to 100; impact types in the allowed set; watchlist XOR. These fail at write time, which is where you want them. Nothing to build.

**Tier 2 — shape (a row exists but is unusable).** These are the ones that bite, because a half-built impact tree looks fine to the database and broken to a user.

| Check | Assertion | Severity |
|---|---|---|
| Events have branches | every event ≤7 days old has ≥1 `event_sector_impacts` row | **block** |
| Branches have leaves | every `event_sector_impacts` row has ≥1 `event_company_impacts` row, or an explicit "no listed companies" explanation | **block** |
| Explanations are real | no `explanation` shorter than 20 chars in either impacts table | **block** |
| Companies resolve | no `event_company_impacts.company_id` pointing at an inactive company | warn |
| Scores have breakdowns | no `confident_scores` row with `breakdown = '[]'` or null | **block** |
| Buckets are exclusive | no company with a bucket but no `bucket_explanation` | warn |
| Prices are sane | no active company with `current_price` null or ≤ 0 | warn |

**Tier 3 — freshness and anomaly (the data is well-formed but wrong or stale).** These catch a provider silently returning empty results, which looks identical to "quiet news day" until you check.

| Check | Assertion | Severity |
|---|---|---|
| Quote freshness | no active company with `quote_refreshed_at` older than 3 hours | warn |
| Score coverage | ≥90% of active companies have a score from the last 24h | warn |
| Sentiment coverage | ≥60% of active companies have a `news` pulse from the last 48h | warn |
| Event volume | today's new-event count within 5× and 0.2× of the trailing 7-day mean | warn |
| Fundamentals cycle | no active company with `fundamentals_refreshed_at` older than 10 days | warn |
| **LLM drop rate** | `dropped_tickers / proposed_tickers` under 10% for the run | **block** |
| **LLM call volume** | run's Anthropic call count under the configured ceiling | **block** |

The last two are your prompt-drift canaries. A rising drop rate means the model is inventing tickers — that is the single most important number in the whole pipeline, and it is free to compute since the universe gate (§2.7) already counts it.

### Where it runs and what "block" means

Add a `validate` stage that depends on everything, runs last, and writes its results into `pipeline_runs.stages['validate']`. Warnings log and increment counters. Blocks need somewhere to stop, and at this scale a full staging-and-swap is overkill — but the differentiator deserves one cheap gate:

```sql
ALTER TABLE events ADD COLUMN published boolean NOT NULL DEFAULT false;
CREATE INDEX events_published_recent_idx ON events (published, published_at DESC);
```

The `events` and `impact_flow` stages write with `published = false`. The `validate` stage flips it to `true` only for events that pass every Tier-2 block check. `GET /api/events` and the homepage feed filter on `published`. Roughly ten lines, and it means a malformed impact tree is invisible rather than embarrassing — which matters most on the one screen the whole project is judged by.

Everything else (scores, prices, sentiment) writes straight through: a stale score labeled with its `captured_at` is honest, and hiding it would leave the Company Detail screen emptier than it needs to be.

### Implementation

Keep them as plain SQL in one module — readable by anyone on the team, no framework:

```python
CHECKS: list[Check] = [
    Check(
        name="events_have_sector_branches",
        severity="block",
        sql="""SELECT e.id FROM events e
               WHERE e.published_at > now() - interval '7 days'
                 AND NOT EXISTS (SELECT 1 FROM event_sector_impacts
                                 WHERE event_id = e.id)""",
        # a check FAILS if the query returns rows; the ids are the offenders
    ),
    ...
]
```

Return the offending ids, not just a count — when a check fails at 3 a.m. you want to know *which* event, and a bare `False` sends you back to psql.

Run the same checks against the seed dataset in CI. Seeds that fail your own quality gates are seeds that will make the demo look broken (`database/seeds/TODO.md` wants "a believable Event Impact Flow" — this is how you enforce "believable" mechanically).

---

# PART 3 — Build order for your track

Mapped to the milestones in [build-plan.md](build-plan.md). Each step ends somewhere you could stop.

| # | Do | Ends when |
|---|---|---|
| 1 | Alembic + docker-compose Postgres + Tier 0/2/3/5 tables (sectors, companies, pipeline_runs, raw_documents, events, impacts) | `alembic upgrade head` / `downgrade base` both pass in CI |
| 2 | `RunContext`, registry, orchestrator, advisory lock, `pipeline_runs` writing | `python -m pipeline.run --cadence hourly` runs zero stages and logs a clean run row |
| 3 | `news` stage + `BudgetedClient` + fixtures | Real headlines land in `raw_documents`; running twice writes nothing new |
| 4 | `events` + `impact_flow` stages (the walking skeleton's core) | An event row with a populated 2-level impact tree, unknown tickers dropped |
| 5 | Seed script (~20 tickers, 5 sectors) + the 10-event eval fixture set | Eval harness runs and scores |
| 6 | Tier 4/6 tables + `market_data` (batched quotes, rolling fundamentals) + `scoring` | Company Detail has a real score with a real breakdown (milestone M-B) |
| 7 | `buckets` (**after the ADR-008 vote**) + Railway cron hourly | The app refills itself unattended (M-C) |
| 8 | Tier 1 tables handed to Hong for auth; `sentiment`, `social`, `consensus` stages; `retention` | M-D / M-E |

**Two things to settle before step 7 that aren't yours alone:** the ADR-008 bucket vote (it determines what the `buckets` stage actually computes) and the NewsAPI-vs-GNews pick (it determines the `news` client, though the interface is identical either way).
