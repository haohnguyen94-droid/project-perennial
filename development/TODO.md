# `development/` — TODO

All code. **M5 is active.** Don't start coding until decisions below are locked.

**Primary owners:** `@aalind @jaden`

---

## Decisions to lock at next meeting

These block everything downstream:

- [ ] **Frontend:** React Native (mobile) vs React (web)
- [ ] **Backend:** Node.js vs Python (Python likely better for AI/ML, Node likely faster to ship)
- [ ] **Database:** PostgreSQL confirmed; add Redis caching? (recommended for Confident Score caching)
- [ ] **Hosting:** AWS / GCP / Vercel / Railway / self-hosted
- [ ] **Auth:** OAuth + JWT vs Auth0/Clerk
- [ ] **MVP screen subset** — proposed cut in root `../TODO.md`
- [ ] **Risk Comfort onboarding** — in or out? (M4 doc says yes, IA says no)

Lock decisions in `../docs/technical-specs/DECISIONS.md`.

---

## Folder map

| Folder | Purpose | TODO |
|--------|---------|------|
| `backend/` | Server, APIs, business logic, AI services | [TODO](backend/TODO.md) |
| `frontend/` | UI, screens, components | [TODO](frontend/TODO.md) |
| `database/` | Schemas, migrations, seeds | [TODO](database/TODO.md) |
| `shared/` | Types and config used by both FE and BE | [TODO](shared/TODO.md) |

---

## Build order

1. **Decisions locked** (above)
2. **`database/`** — schema first; everything else builds on it
3. **`shared/`** — define types so FE and BE agree
4. **`backend/`** — API endpoints stubbed with mock data
5. **`frontend/`** — screens built against the stubbed API
6. **AI services** — sentiment + Confident Score + Event Impact Flow plugged in last

This order lets people work in parallel.

---

## What we are NOT building (per M4)

- ❌ Screening / financial filtering screens
- ❌ Full financial statements / ROE / valuation multiples (only simplified Finance section under "Why This Company")
- ❌ Multi-tab navigation (Research / Portfolio / Watchlist as separate top-level tabs)
- ❌ Portfolio tracking / holdings / allocation visualization
- ❌ Weekly Digest endpoint or screen
- ❌ Separate Search results screen (search is part of Homepage)
- ❌ Contextual Learning Overlay backend (no `/api/learn/:term`)
- ❌ Private market / pre-IPO endpoints

Push back if any of these creep back in.
