# `backend/src/middleware/` — TODO

Functions that run on every request before route handlers.

**Owner:** `@aalind` (infra), `@hong` (auth)

---

## Middleware to build

- [ ] `auth.{js,ts,py}` — verify JWT, attach user; reject if invalid — `@hong`
- [ ] `validation.{js,ts,py}` — run request body/params against schema
- [ ] `error-handler.{js,ts,py}` — catch all errors, return `{ error, message, code }`
- [ ] `rate-limit.{js,ts,py}` — basic rate limit per IP/user
- [ ] `logging.{js,ts,py}` — log method, path, status, duration
- [ ] `cors.{js,ts,py}` — allow frontend origin
- [ ] `disclaimer-injector.{js,ts,py}` — append disclaimer to AI-driven responses (Confident Score, Sentiment, Event Impact Flow)

---

## Register order

1. CORS
2. Logging
3. Rate limit
4. Auth (protected routes only)
5. Validation (per route)
6. Route handler
7. Error handler (last)
