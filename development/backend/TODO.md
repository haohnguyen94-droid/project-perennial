# `development/backend/` — TODO

Server code, APIs, business logic, AI services.

**Owner:** `@aalind`

---

## Setup

- [ ] Decide language: Node.js (Express/Fastify/Nest) or Python (FastAPI/Django)
- [ ] Initialize project (`package.json` or `pyproject.toml`)
- [ ] Set up linter + formatter
- [ ] Set up `.env.example` with all required env var names
- [ ] Set up dev server with hot reload
- [ ] Add `README.md` to this folder explaining how to run backend locally

---

## Folder map (under `src/`)

| Folder | TODO |
|--------|------|
| `api/` | [TODO](src/api/TODO.md) |
| `models/` | [TODO](src/models/TODO.md) |
| `services/` | [TODO](src/services/TODO.md) |
| `middleware/` | [TODO](src/middleware/TODO.md) |
| `utils/` | [TODO](src/utils/TODO.md) |

---

## API endpoints to implement (aligned to M4 IA)

### Auth
- [ ] `POST /api/auth/signup`
- [ ] `POST /api/auth/login`
- [ ] `POST /api/auth/logout`
- [ ] `POST /api/auth/refresh`
- [ ] `POST /api/auth/change-password` — for Setting → Change Your Password

### Onboarding
- [ ] `POST /api/onboarding/interests` — save Choose Interest selections (returns Confirmation summary)
- [ ] `POST /api/onboarding/complete` — mark user as past onboarding

### Homepage data
- [ ] `GET /api/homepage` — single bundle endpoint returning Affordable & Growing list, Popular & Stable list, and Insight (current events) for the user. Reduces round-trips on the most-loaded screen.
- [ ] `GET /api/homepage/affordable-growing` — paginated list of companies in this tab
- [ ] `GET /api/homepage/popular-stable` — paginated list of companies in this tab
- [ ] `GET /api/search?q=` — Homepage Search Bar autocomplete (companies + events)

### Insight / Events
- [ ] `GET /api/events` — list events (used by Insight section)
- [ ] `GET /api/events/:id` — Event Detail with all 5 sections: What Happened, Effects Markets, Affected Companies, Sentiments, Related Events
- [ ] `GET /api/events/:id/sources` — News / Social Media / Analyst sources for the event

### Company Detail
- [ ] `GET /api/companies/:id` — full Company Detail bundle (Confident Score, Breakdown, Event Exposure, Sentiment, Analyst Outlook, Price breakdown, Sentiment Pulse, Why This Company, Finance)
- [ ] `GET /api/companies/:id/sentiment-pulse?source=news|social|analyst` — sentiment breakdown per tab
- [ ] `GET /api/companies/:id/why` — Why This Company → Key Reasons + Finance chart data

### Watchlist
- [ ] `GET /api/user/watchlist?filter=all|companies|sectors` — list watchlist with filter tab
- [ ] `POST /api/user/watchlist` — add (supports adding single company OR a sector OR an event's "Add all" bulk action)
- [ ] `DELETE /api/user/watchlist/:id` — remove

### Setting + Profile
- [ ] `GET /api/user/profile` — Name, Email, Investment
- [ ] `PUT /api/user/profile`
- [ ] `GET /api/user/notification-preferences`
- [ ] `PUT /api/user/notification-preferences`
- [ ] `PUT /api/user/preferences` — Update Preference (interests)

### Privacy (CCPA / GDPR — still required even though no dedicated screen)
- [ ] `GET /api/user/data` — full data export
- [ ] `DELETE /api/user/data` — delete account + grace period

---

## Endpoints REMOVED from earlier plan

- ❌ `GET /api/market/health` — Market Health Dashboard rejected
- ❌ `GET /api/market/sectors` — same
- ❌ `GET /api/user/digest` — Weekly Digest rejected
- ❌ `GET /api/learn/:term` — Contextual Learning Overlay rejected

---

## Every endpoint should

- [ ] Validate input with a schema (Zod / Joi / Pydantic)
- [ ] Return consistent error shape: `{ error, message, code }`
- [ ] Be documented in `../docs/api-docs/`
- [ ] Have at least one integration test in `../../testing/integration/`
- [ ] Auth-protected endpoints (`/api/user/*`, `/api/onboarding/*`) require valid JWT
