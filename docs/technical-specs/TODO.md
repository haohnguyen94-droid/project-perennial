# `docs/technical-specs/` — TODO

Architecture and decision documents.

**Owner:** `@aalind`

---

## Status

- [x] `ARCHITECTURE.md` — draft exists
- [ ] Updated post-M4 to reflect locked scope

---

## Documents to write

### `ARCHITECTURE.md` (update existing)
- [ ] Lock decision: React Native vs React
- [ ] Lock decision: backend language
- [ ] Lock decision: hosting
- [ ] Update API endpoint list to match IA-aligned routes
- [ ] Add deployment diagram

### `DECISIONS.md` (new — ADR-style)
- [ ] Log every architecture / scope / tech decision with date + reasoning
- [ ] Start with the M4 rejections (why no portfolio, no learning overlay, etc.)

### `DATA_SOURCES.md`
- [ ] Financial data API chosen (and why)
- [ ] News API chosen
- [ ] Sentiment sources for News / Social / Analyst tabs
- [ ] Rate limits and pricing per source
- [ ] Failover if a primary source goes down

### `SCORING_FORMULA.md` — `@cohen @aalind`
- [ ] How the 0–100 Confident Score is computed
- [ ] What inputs feed in (market, sentiment, event exposure, analyst outlook)
- [ ] How each input is weighted
- [ ] How the Breakdown text is generated
- [ ] Examples of high / mixed / low scores with their Breakdowns

### `EVENT_IMPACT_FLOW.md` — `@cohen @aalind` ⭐
- [ ] How an event is decomposed into sector impacts
- [ ] How sector impacts are decomposed into company impacts
- [ ] How positive vs negative branches are determined
- [ ] Data shape that the frontend `EventImpactFlow` component consumes
- [ ] Examples (e.g. semiconductor tariff → hurts chip importers, helps domestic producers)

### `SENTIMENT_MODEL.md` — `@cohen`
- [ ] Model used (pretrained, fine-tuned, or rule-based)
- [ ] Per-source: how News / Social / Analyst sentiment is gathered
- [ ] How positive/mixed/negative thresholds are set
- [ ] Top excerpts selection logic
- [ ] Known limitations

### `AUTH_FLOW.md` — `@hong`
- [ ] Signup, login, logout, refresh diagram
- [ ] Token lifetime + refresh policy
- [ ] Password requirements
- [ ] Change Password flow (Setting → Change Your Password)
- [ ] Forgot-password flow
- [ ] Privacy implications of data deletion
