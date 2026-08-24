# `development/database/` — TODO

Database schemas, migrations, seeds.

**Owner:** `@aalind`

---

## Setup

- [x] PostgreSQL confirmed — PG 16 ([ADR-003](../../docs/architecture/decisions/ADR-003-postgres-single-store.md)); local via `development/docker-compose.yml` (host port 5433)
- [x] Decide on Redis caching — **no Redis in v1** ([ADR-007](../../docs/architecture/decisions/ADR-007-no-redis-no-queue.md))
- [x] Pick a migration tool — **Alembic**, scaffolded in `development/backend/` (`alembic.ini`, `migrations/`)
- [x] Document local DB setup — see [`POSTGRES_SETUP.md`](POSTGRES_SETUP.md) in this folder (deep-dive, setup steps, prod plan)

---

## Folder map

| Folder | TODO |
|--------|------|
| `schemas/` | [TODO](schemas/TODO.md) |
| `migrations/` | [TODO](migrations/TODO.md) |
| `seeds/` | [TODO](seeds/TODO.md) |

---

## Build order

1. ~~Define schemas~~ → full DDL in [pipeline-and-schema-guide.md §1.2](../../docs/architecture/pipeline-and-schema-guide.md) (+ amendments in `POSTGRES_SETUP.md` §3)
2. ~~Create initial migration~~ → `20260824034321_initial_content_schema.py` (tiers 0/2/3/5; tested both directions). Tiers 4/6 and user tables land as migrations 002/003.
3. Generate seed data (with realistic events + companies) → `seeds/TODO.md`
4. ~~Run locally to confirm~~ → upgrade → downgrade → upgrade verified against local PG 16; CI gate in `.github/workflows/db-ci.yml`
5. Hook up backend `models/` to match (only `src/models/base.py` exists so far)
