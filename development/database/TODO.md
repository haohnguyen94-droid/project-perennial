# `development/database/` — TODO

Database schemas, migrations, seeds.

**Owner:** `@aalind`

---

## Setup

- [ ] PostgreSQL confirmed
- [ ] Decide on Redis caching (recommended for Confident Score + Sentiment Pulse caching)
- [ ] Pick a migration tool (Prisma / Knex / Sequelize CLI / Alembic / TypeORM)
- [ ] Document local DB setup in this folder's `README.md`

---

## Folder map

| Folder | TODO |
|--------|------|
| `schemas/` | [TODO](schemas/TODO.md) |
| `migrations/` | [TODO](migrations/TODO.md) |
| `seeds/` | [TODO](seeds/TODO.md) |

---

## Build order

1. Define schemas → `schemas/TODO.md`
2. Create initial migration → `migrations/TODO.md`
3. Generate seed data (with realistic events + companies) → `seeds/TODO.md`
4. Run locally to confirm
5. Hook up backend `models/` to match
