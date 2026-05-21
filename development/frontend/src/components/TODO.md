# `frontend/src/components/` — TODO

Reusable UI components. One folder per component (`ComponentName/index.tsx`, optional `.test.tsx`, optional styles).

**Owner:** `@jaden` (build), `@cohen` (Figma spec)

---

## Components to build (1:1 with `../../../design/ui-kit/TODO.md`)

### Score / sentiment / data display
- [ ] `ConfidentScoreBadge/` — 0–100 with traffic-light color (0–39 red / 40–69 yellow/mixed / 70–100 green), explanation tooltip
- [ ] `SentimentPulse/` — 3-tab component (News / Social Media / Analyst), each tab shows positive/mixed/negative breakdown + top excerpts
- [ ] `SentimentIndicator/` — small pill (positive/mixed/negative) used in event Affected Companies list + Watchlist rows
- [ ] `TrafficLightDot/` — green/yellow/red dot used in Affordable & Growing rows

### Price / company data
- [ ] `PriceOverview/` — current price + fair value range + "In range" indicator
- [ ] `WeekRangeBar/` — 52-week range bar with low / avg / current / high markers
- [ ] `RevenueChart/` — 5-year revenue chart (simple bar or line; no candlesticks)

### Insight / Event components (the differentiator)
- [ ] `EventCard/` — collapsed: headline + brief impact + "Show more"
- [ ] `EventImpactFlow/` ⭐ — **the centerpiece visual**. Renders event → branches into affected sectors (positive/negative) → companies. Owner: `@jaden` + `@cohen` reviewing
- [ ] `AffectedCompanyRow/` — name + sector tag + sentiment + price + `+ Watchlist` button
- [ ] `EventSourcesTabs/` — News / Social Media / Analyst source tabs with excerpts
- [ ] `PublicSentimentBar/` — overall event-level sentiment with source breakdown
- [ ] `RelatedEventsList/` — compact list of other relevant events

### Homepage components
- [ ] `HomepageSearchBar/` — autocomplete search bar at top of Homepage
- [ ] `TabSwitcher/` — for "Affordable & Growing" / "Popular & Stable"
- [ ] `CompanyListRow/` — ticker + traffic-light dot + momentum arrow + current price
- [ ] `MomentumArrow/` — ↑ ↓ → indicator

### Watchlist
- [ ] `WatchlistFilterTabs/` — All / Companies / Sectors
- [ ] `WatchlistRow/` — name + sector tag + sentiment + Confident Score (color) + price + View/Remove
- [ ] `WatchlistEmptyState/` — friendly prompt + topic chips (AI, Crypto, Green Energy, Finance)
- [ ] `NewEventBadge/` — red dot for watchlist items with recent activity

### Forms / inputs
- [ ] `Button/` — primary, secondary, ghost, destructive
- [ ] `TextInput/`
- [ ] `Select/`
- [ ] `Toggle/` — for Notification preferences
- [ ] `Checkbox/`
- [ ] `InterestChip/` — multi-select chip for Choose Interest screen

### Layout / nav
- [ ] `Sidebar/` — left nav with Insight / Watchlist / Setting / Profile entries
- [ ] `Header/` — top bar
- [ ] `Card/` — surface with shadow + rounded corners
- [ ] `SectionHeader/` — for "What Happened", "Effects Markets", etc.
- [ ] `ExpandableSection/` — for "Why This Company", event "Show more"

### Feedback / state
- [ ] `Loading/` — spinner or skeleton
- [ ] `EmptyState/` — generic empty placeholder
- [ ] `ErrorState/` — generic error with retry
- [ ] `Disclaimer/` — "AI-generated guidance, not financial advice" line

---

## REMOVED from earlier plan

- ❌ `LearningTooltip` — Contextual Learning Overlay rejected
- ❌ `MarketHealthIndicator` — Market Health Dashboard rejected
- ❌ Components for Weekly Digest / standalone Search page

---

## Build priority

1. `Button`, `Card`, `SectionHeader` (used by everything)
2. `ConfidentScoreBadge`, `TrafficLightDot`, `SentimentIndicator` (used by lots of pages)
3. **`EventImpactFlow`** (hardest + differentiator — build early to find blockers)
4. Homepage list components (`TabSwitcher`, `CompanyListRow`)
5. `SentimentPulse` 3-tab
6. `PriceOverview`, `WeekRangeBar`
7. Watchlist components
8. Settings/Profile components

---

## Conventions

- [ ] One folder per component
- [ ] Components take data via props — no fetching inside
- [ ] Loading / empty / error states everywhere it makes sense
- [ ] Accessibility: roles, labels, contrast, focus
- [ ] Theme tokens only — no raw hex
