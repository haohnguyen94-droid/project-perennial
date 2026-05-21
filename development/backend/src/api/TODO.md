# `backend/src/api/` — TODO

Route handlers — thin layer that validates, calls a service, returns a response.

**Owner:** `@aalind`

---

## Rule: handlers are THIN

Business logic belongs in `../services/`. Handlers should only:

1. Validate request input
2. Call a service
3. Format and return the response
4. Let middleware handle errors (don't try/catch in every route)

---

## Files to create

One file per resource:

- [ ] `auth.{js,ts,py}`
- [ ] `onboarding.{js,ts,py}`
- [ ] `homepage.{js,ts,py}` — the bundle endpoint + Affordable & Growing + Popular & Stable + search
- [ ] `events.{js,ts,py}` — events list, event detail, event sources
- [ ] `companies.{js,ts,py}` — company detail + sentiment pulse + why this company
- [ ] `watchlist.{js,ts,py}`
- [ ] `user.{js,ts,py}` — profile, preferences, notification settings, privacy

Plus:

- [ ] `index.{js,ts,py}` — registers all routes with the app
