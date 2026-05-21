# `backend/src/utils/` — TODO

External API clients and small helpers.

**Owner:** `@aalind`

---

## External API clients

- [ ] `clients/financial-data.{js,ts,py}` — Alpha Vantage / Finnhub / Polygon (pick one)
- [ ] `clients/news-api.{js,ts,py}` — NewsAPI or GNews
- [ ] `clients/reddit.{js,ts,py}` — sentiment source
- [ ] `clients/stocktwits.{js,ts,py}` — sentiment source
- [ ] `clients/analyst-feed.{js,ts,py}` — for the Analyst sentiment tab + Analyst Outlook on Company Detail

Each client wraps fetch/requests, handles auth headers, retries, rate limits, exposes typed methods.

---

## Helpers

- [ ] `date.{js,ts,py}` — date formatting, "X hours ago", week boundaries
- [ ] `text.{js,ts,py}` — truncation, sanitization
- [ ] `logger.{js,ts,py}` — wraps console / Winston / Pino
- [ ] `crypto.{js,ts,py}` — password hashing helpers

---

## Rules

- Pure functions where possible
- No business logic — that's `../services/`
- No HTTP concerns — that's `../api/` or `../middleware/`
