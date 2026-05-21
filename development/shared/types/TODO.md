# `shared/types/` — TODO

Shared TypeScript types FE and BE must agree on.

**Owner:** `@aalind`

---

## Entity types (mirror DB schema)
- [ ] `User`
- [ ] `UserInterest`
- [ ] `Sector`
- [ ] `Company`
- [ ] `Event`
- [ ] `EventSectorImpact`, `EventCompanyImpact`
- [ ] `EventSource`
- [ ] `ConfidentScore`
- [ ] `SentimentPulse`
- [ ] `WhyThisCompany`
- [ ] `WatchlistItem`

## API request/response types
- [ ] `ApiError`
- [ ] `Paginated<T>`
- [ ] `HomepageBundleResponse` — Affordable & Growing + Popular & Stable + Insight
- [ ] `EventDetailResponse` — with all 5 sections + sources
- [ ] `EventImpactFlowData` — the data structure rendered by the flow chart component
- [ ] `CompanyDetailResponse` — full bundle
- [ ] `SentimentPulseResponse` — per-source-type
- [ ] `WatchlistResponse`

## Enums
- [ ] `Sector` — Tech / Energy / Healthcare / Finance / Crypto / etc.
- [ ] `ImpactLevel` — high / medium / low
- [ ] `ImpactType` — positive / negative / neutral
- [ ] `SentimentLabel` — positive / mixed / negative
- [ ] `SourceType` — news / social_media / analyst
- [ ] `TrafficLight` — green / yellow / red
- [ ] `Momentum` — up / down / flat
- [ ] `WatchlistFilter` — all / companies / sectors
- [ ] `WatchlistTargetType` — company / sector

---

## REMOVED from earlier plan

- ❌ `LearningTerm` type
- ❌ `WeeklyDigestResponse`
- ❌ `ExperienceLevel` enum (Risk Comfort / Experience Level — pending decision on whether to ship)

---

## Conventions

- One file per logical group (`user.ts`, `event.ts`, `api.ts`)
- `interface` for object shapes, `type` for unions/aliases
- If a type is only used on one side, **don't put it here** — keep it next to its usage
