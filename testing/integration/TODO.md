# `testing/integration/` — TODO

Tests exercising multiple layers together.

**Owners:** `@aalind` (API), `@jaden` (E2E)

---

## Setup

- [ ] Backend tests run against a **test database** (separate from dev)
- [ ] Each test starts with clean DB state (reset + seed)
- [ ] Use Supertest (Node) or httpx (Python) to hit real endpoints
- [ ] For E2E: Playwright or Cypress

---

## API integration tests

For every endpoint, at minimum:
- Happy path → 200 with expected shape
- Auth failure on protected routes → 401
- Validation failure → 400 with clear error
- Not found → 404

Priority endpoints:
- [ ] `GET /api/homepage` — Affordable & Growing + Popular & Stable + Insight all present
- [ ] `GET /api/events/:id` — all 5 sections present (What Happened, Effects Markets, Affected Companies, Sentiments, Related Events)
- [ ] `GET /api/companies/:id` — full bundle including Confident Score with Breakdown
- [ ] `GET /api/companies/:id/sentiment-pulse?source=news` (then social, then analyst)
- [ ] `GET /api/user/watchlist?filter=companies` (and `sectors`, and `all`)
- [ ] `POST /api/user/watchlist` — single + bulk-add from event
- [ ] `DELETE /api/user/watchlist/:id`
- [ ] `POST /api/auth/signup` + `POST /api/auth/login` round-trip
- [ ] `POST /api/auth/change-password`
- [ ] `DELETE /api/user/data` — actually deletes

---

## End-to-end flows (mirror `../../design/user-flows/USER_FLOWS.md`)

- [ ] **Flow 1** — Get Started → Choose Interest → Confirmation → Homepage
- [ ] **Flow 2** — Insight section → Event Detail → tap Affected Company → Company Detail → add to Watchlist (Use Case 1)
- [ ] **Flow 3** — Search Bar / Homepage row → Company Detail → tap Sentiment Pulse tabs → expand Why This Company → add to Watchlist (Use Case 2)
- [ ] **Flow 4** — Watchlist filter by Sectors → tap row → Company Detail → remove
- [ ] **Flow 5** — Setting → Change Password
- [ ] **Flow 5b** — Profile → view Name / Email / Investment

---

## Conventions

- Group by resource (`events.integration.test.*`, `watchlist.integration.test.*`)
- E2E tests in their own `e2e/` subfolder
- No real external APIs — mock NewsAPI, Reddit, etc. at the boundary
