# `database/schemas/` — TODO

Schema definitions for every table.

**Owner:** `@aalind`

---

## Tables to define

### Auth + users
- [ ] `users` — id (uuid PK), email (unique), password_hash, name, investment_summary, onboarding_completed (bool), created_at, updated_at
- [ ] `user_interests` — id, user_id (FK), interest_type (enum: sector/theme), interest_value
- [ ] `user_notification_preferences` — user_id (PK FK), channels (jsonb), frequency, types_enabled (jsonb)

### Companies + sectors
- [ ] `sectors` — id, name, display_label
- [ ] `companies` — id (uuid PK), name, ticker (unique), sector_id (FK), market_cap, current_price, traffic_light (enum: green/yellow/red), momentum (enum: up/down/flat), last_updated
- [ ] `company_price_snapshots` — id, company_id (FK), captured_at, price, week_52_low, week_52_high, week_52_avg, fair_value_low, fair_value_high
- [ ] `company_financials` — id, company_id (FK), year, revenue (used for 5-year revenue chart)

### Events + Insight
- [ ] `events` — id, headline, summary, source_name, source_url, published_at, impact_level (enum), what_happened (text), effects_markets_summary (text)
- [ ] `event_sector_impacts` — id, event_id (FK), sector_id (FK), impact_type (enum: positive/negative/neutral), explanation
- [ ] `event_company_impacts` — id, event_id (FK), company_id (FK), impact_type, explanation
- [ ] `event_sources` — id, event_id (FK), source_type (enum: news/social_media/analyst), excerpt, url, sentiment

### Scoring + sentiment
- [ ] `confident_scores` — id, company_id (FK), score (int 0-100), breakdown (jsonb), event_exposure_summary, analyst_outlook_summary, captured_at
- [ ] `sentiment_pulses` — id, company_id (FK), source_type (enum: news/social/analyst), positive_pct, mixed_pct, negative_pct, top_excerpts (jsonb), captured_at
- [ ] `why_this_company` — id, company_id (FK), key_reasons (jsonb: array of {reason, explanation}), last_updated

### Watchlist
- [ ] `watchlist_items` — id, user_id (FK), target_type (enum: company/sector), target_id, added_at, has_new_event (bool)

---

## Conventions

- [ ] Every table has `created_at` and `updated_at`
- [ ] Use `uuid` for primary keys
- [ ] Snake_case column names
- [ ] Indexes on FKs + columns used in WHERE clauses
- [ ] Use `jsonb` (not `json`) for flexible columns

---

## REMOVED from earlier plan

- ❌ `learning_terms` table
- ❌ Weekly digest related tables
- ❌ Market health dashboard tables
