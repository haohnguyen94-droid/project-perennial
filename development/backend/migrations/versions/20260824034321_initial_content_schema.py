"""initial content schema

Revision ID: e12d2abbc333
Revises:
Create Date: 2026-08-24 03:43:21.478866+00:00

Tiers 0/2/3/5 of the schema in docs/architecture/pipeline-and-schema-guide.md
§1.2, with the three amendments from development/database/POSTGRES_SETUP.md §3:
'short_interest' in the consensus_signals signal_type CHECK, events.published
from day one, and extensions created first. All constraints are named
(pk_/uq_/ck_/fk_ convention) so future migrations can drop them by name.

Rules (database/migrations/TODO.md): immutable once merged; every migration
reversible; test upgrade AND downgrade before committing.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e12d2abbc333'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_STEPS = [
    "CREATE EXTENSION IF NOT EXISTS citext",
    "CREATE EXTENSION IF NOT EXISTS pg_trgm",

    # ── TIER 0 — reference data (pipeline-written, rarely changes) ──
    """
    CREATE TABLE sectors (
      id            uuid CONSTRAINT pk_sectors PRIMARY KEY DEFAULT gen_random_uuid(),
      name          text NOT NULL CONSTRAINT uq_sectors_name UNIQUE,
      display_label text NOT NULL,
      created_at    timestamptz NOT NULL DEFAULT now(),
      updated_at    timestamptz NOT NULL DEFAULT now()
    )
    """,
    """
    CREATE TABLE companies (
      id            uuid CONSTRAINT pk_companies PRIMARY KEY DEFAULT gen_random_uuid(),
      ticker        text NOT NULL CONSTRAINT uq_companies_ticker UNIQUE,
      name          text NOT NULL,
      sector_id     uuid NOT NULL
                    CONSTRAINT fk_companies_sector_id_sectors
                    REFERENCES sectors(id) ON DELETE RESTRICT,
      market_cap    numeric(24,2),
      current_price numeric(18,4),
      traffic_light text CONSTRAINT ck_companies_traffic_light
                    CHECK (traffic_light IN ('green','yellow','red')),
      momentum      text CONSTRAINT ck_companies_momentum
                    CHECK (momentum IN ('up','down','flat')),
      bucket        text CONSTRAINT ck_companies_bucket
                    CHECK (bucket IN ('affordable_growing','popular_stable')),
      bucket_explanation text,
      is_active     boolean NOT NULL DEFAULT true,
      quote_refreshed_at        timestamptz,
      fundamentals_refreshed_at timestamptz,
      last_updated  timestamptz,
      created_at    timestamptz NOT NULL DEFAULT now(),
      updated_at    timestamptz NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX companies_sector_idx ON companies (sector_id)",
    "CREATE INDEX companies_bucket_idx ON companies (bucket) WHERE is_active",
    """
    CREATE INDEX companies_search_idx ON companies
      USING gin ((ticker || ' ' || name) gin_trgm_ops)
    """,

    # ── TIER 2 — operations ledger (pipeline-written) ──
    """
    CREATE TABLE pipeline_runs (
      id          uuid CONSTRAINT pk_pipeline_runs PRIMARY KEY DEFAULT gen_random_uuid(),
      trigger     text NOT NULL CONSTRAINT ck_pipeline_runs_trigger
                  CHECK (trigger IN ('cron','manual')),
      cadence     text NOT NULL CONSTRAINT ck_pipeline_runs_cadence
                  CHECK (cadence IN ('hourly','daily')),
      status      text NOT NULL CONSTRAINT ck_pipeline_runs_status
                  CHECK (status IN ('running','succeeded','partial','failed')),
      started_at  timestamptz NOT NULL DEFAULT now(),
      finished_at timestamptz,
      stages      jsonb NOT NULL DEFAULT '{}'::jsonb
    )
    """,
    "CREATE INDEX pipeline_runs_recent_idx ON pipeline_runs (started_at DESC)",

    # ── TIER 3 — ingestion staging (pipeline-written, pipeline-read only) ──
    """
    CREATE TABLE raw_documents (
      id           uuid CONSTRAINT pk_raw_documents PRIMARY KEY DEFAULT gen_random_uuid(),
      source_type  text NOT NULL CONSTRAINT ck_raw_documents_source_type
                   CHECK (source_type IN ('news','social_media','analyst')),
      provider     text NOT NULL,
      external_id  text NOT NULL,
      title        text,
      body         text,
      url          text,
      author       text,
      published_at timestamptz,
      payload      jsonb NOT NULL DEFAULT '{}'::jsonb,
      fetched_at   timestamptz NOT NULL DEFAULT now(),
      processed_at timestamptz,
      CONSTRAINT uq_raw_documents_provider_external_id UNIQUE (provider, external_id)
    )
    """,
    """
    CREATE INDEX raw_documents_unprocessed_idx
      ON raw_documents (source_type, published_at DESC) WHERE processed_at IS NULL
    """,
    """
    CREATE TABLE consensus_signals (
      id          uuid CONSTRAINT pk_consensus_signals PRIMARY KEY DEFAULT gen_random_uuid(),
      ticker      text NOT NULL,
      company_id  uuid CONSTRAINT fk_consensus_signals_company_id_companies
                  REFERENCES companies(id) ON DELETE CASCADE,
      signal_type text NOT NULL CONSTRAINT ck_consensus_signals_signal_type
                  CHECK (signal_type IN
                    ('congress_trade','ark_holding','insider_buy','short_interest')),
      dedupe_key  text NOT NULL,
      payload     jsonb NOT NULL,
      observed_at date NOT NULL,
      fetched_at  timestamptz NOT NULL DEFAULT now(),
      CONSTRAINT uq_consensus_signals_signal_type_dedupe_key UNIQUE (signal_type, dedupe_key)
    )
    """,
    """
    CREATE INDEX consensus_company_idx
      ON consensus_signals (company_id, signal_type, observed_at DESC)
    """,

    # ── TIER 5 — insight content (pipeline-written; LLM-generated fields) ──
    """
    CREATE TABLE events (
      id                      uuid CONSTRAINT pk_events PRIMARY KEY DEFAULT gen_random_uuid(),
      slug                    text CONSTRAINT uq_events_slug UNIQUE,
      headline                text NOT NULL,
      summary                 text,
      what_happened           text,
      effects_markets_summary text,
      impact_level            text CONSTRAINT ck_events_impact_level
                              CHECK (impact_level IN ('high','medium','low')),
      source_name             text,
      source_url              text,
      published_at            timestamptz NOT NULL,
      content_hash            text NOT NULL CONSTRAINT uq_events_content_hash UNIQUE,
      published               boolean NOT NULL DEFAULT false,
      pipeline_run_id         uuid CONSTRAINT fk_events_pipeline_run_id_pipeline_runs
                              REFERENCES pipeline_runs(id) ON DELETE SET NULL,
      created_at              timestamptz NOT NULL DEFAULT now(),
      updated_at              timestamptz NOT NULL DEFAULT now()
    )
    """,
    "CREATE INDEX events_recent_idx ON events (published_at DESC)",
    "CREATE INDEX events_published_recent_idx ON events (published, published_at DESC)",
    """
    CREATE TABLE event_sector_impacts (
      id          uuid CONSTRAINT pk_event_sector_impacts PRIMARY KEY DEFAULT gen_random_uuid(),
      event_id    uuid NOT NULL CONSTRAINT fk_event_sector_impacts_event_id_events
                  REFERENCES events(id) ON DELETE CASCADE,
      sector_id   uuid NOT NULL CONSTRAINT fk_event_sector_impacts_sector_id_sectors
                  REFERENCES sectors(id) ON DELETE CASCADE,
      impact_type text NOT NULL CONSTRAINT ck_event_sector_impacts_impact_type
                  CHECK (impact_type IN ('positive','negative','neutral')),
      explanation text NOT NULL,
      CONSTRAINT uq_event_sector_impacts_event_id_sector_id UNIQUE (event_id, sector_id)
    )
    """,
    "CREATE INDEX esi_sector_idx ON event_sector_impacts (sector_id)",
    """
    CREATE TABLE event_company_impacts (
      id            uuid CONSTRAINT pk_event_company_impacts PRIMARY KEY DEFAULT gen_random_uuid(),
      event_id      uuid NOT NULL CONSTRAINT fk_event_company_impacts_event_id_events
                    REFERENCES events(id) ON DELETE CASCADE,
      company_id    uuid NOT NULL CONSTRAINT fk_event_company_impacts_company_id_companies
                    REFERENCES companies(id) ON DELETE CASCADE,
      via_sector_id uuid CONSTRAINT fk_event_company_impacts_via_sector_id_sectors
                    REFERENCES sectors(id) ON DELETE SET NULL,
      impact_type   text NOT NULL CONSTRAINT ck_event_company_impacts_impact_type
                    CHECK (impact_type IN ('positive','negative','neutral')),
      explanation   text NOT NULL,
      CONSTRAINT uq_event_company_impacts_event_id_company_id UNIQUE (event_id, company_id)
    )
    """,
    "CREATE INDEX eci_company_idx ON event_company_impacts (company_id)",
    "CREATE INDEX eci_event_sector_idx ON event_company_impacts (event_id, via_sector_id)",
    """
    CREATE TABLE event_sources (
      id              uuid CONSTRAINT pk_event_sources PRIMARY KEY DEFAULT gen_random_uuid(),
      event_id        uuid NOT NULL CONSTRAINT fk_event_sources_event_id_events
                      REFERENCES events(id) ON DELETE CASCADE,
      raw_document_id uuid CONSTRAINT fk_event_sources_raw_document_id_raw_documents
                      REFERENCES raw_documents(id) ON DELETE SET NULL,
      source_type     text NOT NULL CONSTRAINT ck_event_sources_source_type
                      CHECK (source_type IN ('news','social_media','analyst')),
      excerpt         text NOT NULL,
      url             text,
      sentiment       text CONSTRAINT ck_event_sources_sentiment
                      CHECK (sentiment IN ('positive','mixed','negative'))
    )
    """,
    "CREATE INDEX event_sources_event_idx ON event_sources (event_id, source_type)",
]

# Exact reverse of UPGRADE_STEPS: children before parents, extensions last.
DOWNGRADE_STEPS = [
    "DROP TABLE event_sources",
    "DROP TABLE event_company_impacts",
    "DROP TABLE event_sector_impacts",
    "DROP TABLE events",
    "DROP TABLE consensus_signals",
    "DROP TABLE raw_documents",
    "DROP TABLE pipeline_runs",
    "DROP TABLE companies",
    "DROP TABLE sectors",
    "DROP EXTENSION IF EXISTS pg_trgm",
    "DROP EXTENSION IF EXISTS citext",
]


def upgrade() -> None:
    for step in UPGRADE_STEPS:
        op.execute(sa.text(step))


def downgrade() -> None:
    for step in DOWNGRADE_STEPS:
        op.execute(sa.text(step))
