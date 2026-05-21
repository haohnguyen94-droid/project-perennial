# `backend/src/services/` — TODO

Business logic — the heart of Perennial's intelligence.

**Owners:** `@aalind` (architecture), `@cohen` (sentiment + scoring + Event Impact Flow)

---

## Services to build

### Event Processing Service — `event-processor.{js,ts,py}`
- [ ] Ingest news/events from selected APIs (NewsAPI, GNews, etc.)
- [ ] Deduplicate similar headlines
- [ ] Classify events by **sector** and **company** impact
- [ ] Generate plain-language "What Happened" summaries (likely via LLM)
- [ ] Generate "Effects Markets" explanation
- [ ] Schedule: pull every N minutes

### Event Impact Flow Service — `event-impact-flow.{js,ts,py}` ⭐
- [ ] **This is the differentiator.** Given an event, produce the data for the flow chart:
  - Event node → list of affected sectors (with +/- impact)
  - Each sector → list of affected companies (with +/- impact)
  - Explanation strings at every node
- [ ] Owner: `@cohen` with `@aalind`
- [ ] Document the logic in `../../../docs/technical-specs/EVENT_IMPACT_FLOW.md`

### Sentiment Analysis Service — `sentiment.{js,ts,py}`
- [ ] Aggregate sentiment from **3 distinct sources**: News, Social Media, Analyst
- [ ] Classify each source as positive / mixed / negative with percentages
- [ ] Surface top excerpts per source (used by Sentiment Pulse tabs)
- [ ] Track sentiment over time
- [ ] Owner: `@cohen` (has prior project to build on)

### Confident Score Engine — `confident-score.{js,ts,py}`
- [ ] Combine market data + sentiment + event exposure
- [ ] Produce 0–100 score per company
- [ ] **Generate Breakdown** (the contributing factors shown on Company Detail)
- [ ] Generate Event Exposure summary
- [ ] Generate Analyst Outlook summary
- [ ] Update near-real-time when inputs change
- [ ] Document formula in `../../../docs/technical-specs/SCORING_FORMULA.md`

### Why This Company Service — `why-this-company.{js,ts,py}`
- [ ] Generate Key Reasons list (e.g. "strong revenue growth", "undervalued")
- [ ] Pull Finance data (5-year revenue) for the expandable chart

### Homepage Service — `homepage.{js,ts,py}`
- [ ] Compose the Homepage bundle (Affordable & Growing, Popular & Stable, current Insight events)
- [ ] Filter Affordable & Growing list (criteria: lower price + positive momentum)
- [ ] Filter Popular & Stable list (criteria: high market cap + steady momentum)
- [ ] Determine traffic-light color for each company
- [ ] Determine momentum arrow direction

### Watchlist Service — `watchlist.{js,ts,py}`
- [ ] Add company / sector / bulk-add from event
- [ ] Compute "has new event" flag for each item
- [ ] Filter by All / Companies / Sectors

### Personalization Service — `personalization.{js,ts,py}`
- [ ] Manage user interest profiles
- [ ] Filter events and companies by relevance to user interests
- [ ] Apply preferences from Update Preference setting

### Auth Service — `auth.{js,ts,py}` — `@hong`
- [ ] Signup, login, logout, refresh
- [ ] Change password (Setting → Change Your Password)
- [ ] Password hashing (bcrypt/argon2)

### Search Service — `search.{js,ts,py}`
- [ ] Autocomplete for the Homepage Search Bar
- [ ] Search companies + events
- [ ] No separate search results screen — search returns enough to navigate directly

---

## REMOVED from earlier plan

- ❌ Weekly digest content generation
- ❌ Learning term lookup service
- ❌ Market Health dashboard service

---

## Conventions

- [ ] Services are framework-agnostic — no HTTP concerns
- [ ] Services call models in `../models/` and external clients in `../utils/`
- [ ] Every "explainable" output (score, sentiment, impact) **must include the explanation string**, not just the number
- [ ] All AI/ML outputs include a disclaimer field usable by the frontend
