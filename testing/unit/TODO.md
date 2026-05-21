# `testing/unit/` — TODO

Tests for individual functions and components in isolation.

**Owners:** `@aalind` (backend), `@jaden` (frontend), `@cohen` (AI logic)

---

## Setup

- [ ] Pick framework: Jest/Vitest (JS) or pytest (Python)
- [ ] Add `npm test` (or `pytest`) script
- [ ] Configure coverage reporting

---

## Backend unit tests

For every file in `../../development/backend/src/services/`:

- [ ] `event-processor.test.*` — fake news input → correct event objects
- [ ] `event-impact-flow.test.*` ⭐ — fake event → correct sector + company branches with explanations
- [ ] `sentiment.test.*` — text → correct classification per source type
- [ ] `confident-score.test.*` — inputs → expected score + Breakdown
- [ ] `why-this-company.test.*` — generates plausible Key Reasons
- [ ] `homepage.test.*` — filters into Affordable & Growing vs Popular & Stable correctly
- [ ] `watchlist.test.*` — add/remove/filter
- [ ] `personalization.test.*` — filters by interests
- [ ] `auth.test.*` — hashing, token generation, validation
- [ ] `search.test.*` — autocomplete returns relevant matches

For utils:
- [ ] `date.test.*`
- [ ] `text.test.*`
- [ ] `crypto.test.*`

---

## Frontend unit tests

For every component in `../../development/frontend/src/components/`:

- [ ] Renders without crashing
- [ ] Renders correct text/values from props
- [ ] Handles loading/empty/error states

Key components needing strong tests:
- [ ] `ConfidentScoreBadge` — score → correct color band
- [ ] `SentimentPulse` — switches between News / Social / Analyst tabs correctly
- [ ] `EventImpactFlow` ⭐ — given mock data, renders all branches with correct +/- styling
- [ ] `AffectedCompanyRow` — shows sentiment indicator, current price, watchlist button
- [ ] `WatchlistFilterTabs` — switching filters changes displayed items
- [ ] `WatchlistEmptyState` — topic chips work
- [ ] `WeekRangeBar` — markers positioned correctly

For utils:
- [ ] `score-color.test.*` — every score range → right color
- [ ] `format.test.*` — number formatting edge cases
- [ ] `date.test.*` — "X hours ago" logic

---

## Conventions

- One test file per source file
- Test names read like sentences
- Mock anything external (DB, network, time)
- Tests are deterministic
