# `frontend/src/utils/` — TODO

Small helpers used across the frontend.

**Owner:** `@jaden`

---

## Helpers

- [ ] `api.{ts,js}` — central API client (base URL, auth header, error handling)
- [ ] `date.{ts,js}` — "2 hours ago", "last Monday"
- [ ] `format.{ts,js}` — number formatting ($1.2B, 72/100), text truncation
- [ ] `score-color.{ts,js}` — `scoreToColor(score)` → theme color
- [ ] `sentiment-color.{ts,js}` — sentiment → theme color
- [ ] `momentum-icon.{ts,js}` — up/down/flat → arrow icon name
- [ ] `validators.{ts,js}` — email, password strength

---

## Rules

- Pure functions, no React state, no DOM
- Easy to unit-test
- If used only in one component, keep next to that component instead
