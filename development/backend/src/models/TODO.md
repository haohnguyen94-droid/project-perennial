# `backend/src/models/` — TODO

Data model definitions.

**Owner:** `@aalind`

---

## Models to define (matches `../../database/schemas/`)

### Core
- [ ] `User` — id, email, password_hash, name, investment_summary, created_at, updated_at, onboarding_completed
- [ ] `UserInterest` — user_id, interest_type (sector/theme), interest_value
- [ ] `UserNotificationPreferences` — user_id, channel, frequency, types_enabled (jsonb)

### Companies & sectors
- [ ] `Company` — id, name, ticker, sector, market_cap, current_price, traffic_light (green/yellow/red), momentum (up/down/flat)
- [ ] `Sector` — id, name, display_label (e.g. "Tech", "Energy")
- [ ] `CompanyPriceSnapshot` — for 52-week range and current/avg/high/low markers
- [ ] `CompanyFinancials` — 5-year revenue data for the "Finance" expandable in Why This Company

### Insight
- [ ] `Event` — id, headline, summary, source_name, source_url, published_at, impact_level, what_happened, effects_markets_summary
- [ ] `EventCompanyImpact` — event_id, company_id, impact_type (positive/negative/neutral), explanation
- [ ] `EventSectorImpact` — event_id, sector_id, impact_type, explanation (used by Effects Markets and the Event Impact Flow chart)
- [ ] `EventSource` — event_id, source_type (news/social_media/analyst), excerpt, url, sentiment

### Scoring & sentiment
- [ ] `ConfidentScore` — company_id, score (0–100), factors_jsonb (Breakdown contents), event_exposure_summary, analyst_outlook_summary, captured_at
- [ ] `SentimentPulse` — company_id, source_type (news/social/analyst), positive_pct, mixed_pct, negative_pct, top_excerpts_jsonb, captured_at
- [ ] `WhyThisCompany` — company_id, key_reasons_jsonb (list of {reason, explanation})

### Watchlist
- [ ] `WatchlistItem` — id, user_id, target_type (company/sector), target_id, added_at, has_new_event_flag

---

## Conventions

- [ ] One file per model
- [ ] Each model exports its schema/class plus helper queries
- [ ] Heavy logic lives in `../services/`
- [ ] If TypeScript, publish shared types to `../../shared/types/`
