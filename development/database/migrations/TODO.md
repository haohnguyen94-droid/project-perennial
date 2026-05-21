# `database/migrations/` — TODO

Versioned schema changes.

**Owner:** `@aalind`

---

## Setup

- [ ] Pick migration tool, document in `../README.md`
- [ ] Configure to read DB connection from env vars
- [ ] Track migrations in git

---

## Conventions

- [ ] Filename: `YYYYMMDDHHMMSS_short_description.{sql,js,ts,py}`
- [ ] **Migrations are immutable.** Never edit one after commit. Write a new one.
- [ ] Every migration is reversible — include `down()` or rollback SQL
- [ ] Test both directions before committing

---

## Initial migrations

- [ ] All tables from `../schemas/`
- [ ] Indexes for hot paths (later, once we know which paths are hot)
