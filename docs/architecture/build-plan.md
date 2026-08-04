# Perennial — Build Plan

**Status:** Proposed (Phase 4 deliverable) · **Date:** 2026-08-03
**Timebox:** ~5 months of runway exists, but per the team's instruction the plan is sequenced by milestone, not calendar date. Order matters; dates don't.

---

## 0. The walking skeleton — prove the risky part first

The riskiest technical bet in Perennial is not auth, not CRUD, not charts. It is:

> **Can Claude Sonnet reliably turn a real news event into a correct, beginner-readable Event Impact Flow (event → sectors ± → companies ±, with explanations), constrained to our ticker universe, cheaply enough to run hourly?**

If that works, Perennial works — it's the differentiator (`TODO.md`: "THE differentiator — must work"). If it doesn't, we need to know in week 2, not month 4, because the fallback (heavier curation, template-driven flows) changes the pipeline design. `frontend/src/components/TODO.md` already agrees: "build Event Impact Flow component first — it's the hardest + the differentiator."

**The thinnest end-to-end slice** (no auth, no onboarding, no watchlist, hardcoded demo user):

1. Repo scaffolding: FastAPI app + Alembic + docker-compose Postgres + CI (lint/test).
2. Migration for the minimal tables: `sectors`, `companies`, `raw_documents`, `events`, `event_sector_impacts`, `event_company_impacts`, `pipeline_runs`.
3. Seed ~20 tickers across 5 sectors (subset of the Q7 universe).
4. Pipeline stages 3+5+6 only: fetch ~10 real headlines (or a fixtures file — works offline) → cluster → **Claude Sonnet structured-output call** → event + impact tree upserted, with the anti-hallucination gate (unknown tickers dropped).
5. `GET /api/events` + `GET /api/events/:id` returning the nested `impact_tree`.
6. React SPA with exactly two screens: event list → Event Detail rendering **`EventImpactFlow`** from live API data.
7. **Eval harness (the actual point):** 10 hand-picked historical events with team-agreed expected impacts (Bryan curates — e.g. the semiconductor-tariff example from `docs/technical-specs/TODO.md`). Script runs the pipeline against them and diffs direction (+/−) per sector/company against expectations. This artifact persists as the regression suite for every later prompt change.

**Skeleton exit criteria:** ≥8/10 eval events produce directionally-correct, plausibly-explained flows; cost per event ≤ ~$0.05; the flow renders legibly on a 375-px viewport (the wireframe width, `design/wireframes/figma-exports/TODO.md`).

---

## 1. Milestones after the skeleton — each independently demoable

Each milestone ends with something you can put in front of the class. P0/P1/P2 labels reference the MVP cut in root `TODO.md` (ASSUMPTION A1).

| # | Milestone | Scope | Demo moment |
|---|-----------|-------|-------------|
| **M-A** | Walking skeleton (above) | Pipeline stages 3/5/6 + 2 screens + eval harness | "Watch a real headline become an impact tree" |
| **M-B** | **Company Detail + scores** (P0) | Stage 1 (FMP quotes/fundamentals) + stage 8 (deterministic score formula → `SCORING_FORMULA.md`, LLM breakdown text) + `GET /api/companies/:id` + Company Detail page (`ConfidentScoreBadge`, Breakdown, `PriceOverview`, `WeekRangeBar`, `RevenueChart`) | "Tap an affected company, see its explained score" |
| **M-C** | **Homepage + buckets + hourly cadence** (P0) | ADR-008 vote implemented; stage 9; `GET /api/homepage` bundle + search; `TabSwitcher`/`CompanyListRow`; Railway cron live hourly; `data_as_of` surfaced | "The app fills itself every hour" |
| **M-D** | **Auth + onboarding + personalization** (P0) | Signup/login/refresh/change-password (Hong), Get Started → Choose Interest → Confirmation, interest-ranked Insight feed, route guards | "Two users see different homepages" |
| **M-E** | **Watchlist + sentiment pulse** (P1 + P2 partial) | Watchlist CRUD + empty state + `has_new_event` badge; stages 4+7 (news sentiment first, then Cohen's YouTube social source, then Finnhub analyst) — Sentiment Pulse ships tabs incrementally, matching the P2 note "ship with 1 tab first" | "Save companies; see three-source sentiment" |
| **M-F** | **Settings/profile + privacy + hardening** (P1/P2) | Settings (notifications prefs UI, change password, logout), Profile stub, data export + delete-with-grace, retention jobs, rate limiting, disclaimer injection everywhere, E2E tests for Flows 1–5 (`testing/integration/TODO.md`) | "The boring screens work; the privacy story is real" |
| **M-G** | **User testing + polish** | Freeze features; run the 5–8-tester protocol from `testing/user-testing/TODO.md`; fix blockers; seed-data quality pass (Bryan); M5 writeup + recorded demo | The M5 deliverable itself |

Dependencies are top-to-bottom, but M-D (auth) and M-E (sentiment stages) can proceed in parallel once M-C lands — they touch disjoint code (Hong+Jaden vs Cohen+Aalind).

---

## 2. Deliberately NOT in v1 — and the seams that keep the door open

| Not building | Why | Seam left so it's not a rewrite |
|---|---|---|
| **Notification delivery** (email/push) | No channel specified anywhere in the repo; demo scale has no one to notify | `user_notification_preferences` table + Settings UI ship anyway; `has_new_event` flag is the trigger a future digest job would consume |
| **Risk Comfort onboarding** (ASSUMPTION A2) | IA is locked without it | `user_interests.interest_type` is an open enum — adding `risk_level` is one migration + one screen |
| **Redis / server-side caching** | Postgres over 150 tickers is microseconds | ADR-007: composed read paths live in service functions — a cache decorator drops in without API changes |
| **Real-time / websockets** | Hourly data (Q5) | `data_as_of` already in every bundle; polling interval is a frontend constant |
| **Admin UI** | Operator = CLI at this scale | Pipeline CLI (`--stage`, `--dry-run`) + `pipeline_runs` table are the hooks an admin page would render |
| **Multi-provider failover** (`DATA_SOURCES.md` wants failover) | One provider per need is enough for a demo | Per-source client interface (`clients/`) means a fallback provider is a second implementation, not a refactor |
| **Mobile app (React Native)** | Q1 decision | Mobile-first responsive CSS + the OpenAPI-generated client keep a future RN app as a second consumer of the same API |
| **Everything on the M4 rejected list** (screeners, portfolio, digest, learning overlay, market health, standalone search) | Explicitly rejected — `TODO.md` says "push back if these creep back in" | None needed. The rejection is the point. |

---

## 3. Top risks, ranked, with early signals

| # | Risk | Early signal it's materializing | Mitigation |
|---|------|--------------------------------|------------|
| 1 | **LLM impact-flow quality** — hallucinated tickers, wrong direction, jargon-laden explanations; the differentiator underwhelms | Skeleton eval scores <8/10; explanations need hand-editing before every demo | Structured outputs + universe-constrained prompts + eval harness in CI (re-run on every prompt change); fallback: curated template flows for the demo set while prompts improve |
| 2 | **Free-tier rate limits vs hourly cadence** — FMP 250 req/day (`fmp.py` header), News ~100/day vs 24 runs/day | 429s in `pipeline_runs`; `data_as_of` gaps; quota exhausted by mid-day | Per-source daily budget table enforced in clients; hourly = news+quotes only (batched), fundamentals/consensus daily; if budgets still bind, drop to 2-hourly news — Q5's "hourly" is a target, not a contract |
| 3 | **Bucket semantics stay unresolved** (the ADR-008 vote never happens) — homepage lists contradict the marketing story; Hao's pipeline and the homepage service compute different truths | Same ticker appears in both buckets; teammates describe the buckets differently in the same meeting | Force the vote at the next Monday meeting (it's already on the `DECISIONS.md` agenda); ADR-008 contains a concrete default so "no decision" still yields a consistent v1 |
| 4 | **Integration drift** — work continues on personal branches against differing assumptions (this already happened: `main` says "PostgreSQL confirmed" while `cohen-working` shipped Firestore) | Branches >2 weeks unmerged; code landing in folders that contradict the TODO conventions (also already happened: scraper in `src/api/`, uploader in `src/middleware/`) | Merge-to-main weekly rule; the walking skeleton creates the shared trunk everyone rebases onto; folder conventions enforced in review |
| 5 | **YouTube pipeline fragility / ToS** — yt-dlp blocks, IP rate-limits, or the team decides the gray area is unacceptable | Rising 429/abandon counts in Cohen's `status.json` equivalents; transcript volume trending to zero | Sentiment degrades gracefully to 2 sources (news+analyst) — Sentiment Pulse tabs ship incrementally by design; decision point documented as accepted-risk in ADR-009 |
| 6 | **Anthropic spend creep** — regeneration loops or unbounded reprocessing | Daily spend >$2 (check console); same `content_hash` reprocessed in logs | Hash-gating (events + score text), Message Batches for bulk regen (50% off), per-run LLM call cap with alert; worst case: cadence for LLM stages drops to daily while fetch stays hourly |
| 7 | **Scope creep re-admitting rejected features** | PRs adding `/api/market/health`, digest tables, portfolio fields | The rejected list is codified in three TODOs; reviewers cite it; this build plan's §2 is the fourth citation |
| 8 | **Single-point knowledge** — Aalind owns schema+API+pipeline skeleton alone | PRs only Aalind can review; bus-factor jokes | Pairing on M-A; every service has a second reader; ADRs (this folder) externalize the reasoning |

---

## 4. Working agreements the plan assumes

- **Decisions land in `docs/architecture/decisions/`** (this folder) — the `DECISIONS.md` log the repo planned, upgraded to ADR files; meeting notes link to them (`docs/meeting-notes/TODO.md` convention).
- **Tests ride along, not after** (`testing/TODO.md`: "Write tests as you write code") — the eval harness is a test suite from day one.
- **Seeds stay demo-quality** — Bryan owns making `seeds/` content believable (`database/seeds/TODO.md` assigns realistic content to `@bryan`); the demo is only as good as its worst impact flow.
- **The IA is law** — screens ship 1:1 with `design/information-architecture/TODO.md`; deviations get flagged to Cohen before code (per `frontend/src/pages/TODO.md`).
