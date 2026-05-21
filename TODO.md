# Perennial — Master TODO (v2 — post-M4)

**Team: Asian Boiz** | CSULB Senior Project, Spring 2026
Last updated: after M4 submission (04/27/2026)

> Every major folder also has its own `TODO.md`. Use this file for the
> big picture; use the folder-level TODOs when you're working in that area.

---

## How to use these TODOs

1. **Pick a folder you own** based on your role
2. **Open that folder's `TODO.md`** — it lists exactly what goes inside
3. **Check off items** as you finish them. Commit the updated TODO.md with your work
4. **If something is missing**, add it to the relevant folder's TODO

**Owner tags:** `@hong` `@bryan` `@aalind` `@jaden` `@cohen` `@all`
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

---

## Folder index

| Folder | Owner(s) | What's in there |
|--------|----------|-----------------|
| [`milestones/TODO.md`](milestones/TODO.md) | `@hong @bryan` | M1–M5 academic deliverables |
| [`design/TODO.md`](design/TODO.md) | `@cohen @jaden` | Wireframes, IA, UI kit, prototypes |
| [`development/TODO.md`](development/TODO.md) | `@aalind @jaden` | Frontend, backend, database |
| [`docs/TODO.md`](docs/TODO.md) | `@hong @bryan` | Research, meeting notes, specs |
| [`assets/TODO.md`](assets/TODO.md) | `@cohen` | Branding, logos, marketing |
| [`testing/TODO.md`](testing/TODO.md) | `@all` | Unit, integration, user testing |

---

## Milestone status

| Milestone | Status | Notes |
|-----------|--------|-------|
| M1 — Team Charter | ✅ Done | `milestones/milestone-1/` |
| M2 — User Research | ✅ Done | `milestones/milestone-2/` |
| M3 — Market Research | ✅ Done | `milestones/milestone-3/` |
| **M4 — Wireframes + IA + Lo-Fi Prototype** | ✅ Done | Submitted 04/27/2026 |
| **M5 — Implementation** | 🔜 **Active** | See `milestones/milestone-5/TODO.md` and `development/TODO.md` |

---

## What the app is, locked from M4

After M4 the team **locked the feature set**. The Information Architecture is
the source of truth — only screens listed there get built. Everything else is
either rejected (see M4 doc) or future roadmap.

### Screens in the IA (the only screens being built)

1. **Get Started** — welcome
2. **Choose Interest** — sector/theme picker
3. **Confirmation** — review choices before entering app
4. **Homepage** — Search Bar + Affordable & Growing + Popular & Stable + Insight section
5. **Event Detail (Insight)** — What Happened, Effects Markets, Affected Companies, Sentiments, Related Events; with News/Social/Analyst sources
6. **Watchlist** — list + empty state
7. **Company Detail** — Confident Score, Breakdown, Event Exposure, Sentiment, Analyst Outlook, Price breakdown, Sentiment Pulse (News/Social/Analyst), Why This Company → Key Reasons & Finance
8. **Setting** — Notification, Your Profile, Update Preference, Change Password, Log Out
9. **Profile** — Name, Email, Investment

### Features REJECTED in M4 (do NOT build)

- ❌ Screening / filtering / small-cap screeners
- ❌ Detailed financial breakdown screens (full statements, ROE tabs, valuation multiples)
- ❌ Multi-tab nav (Research / Portfolio / Watchlist / Profile)
- ❌ Portfolio tracking / holdings / allocation visualization
- ❌ Weekly Digest screen (was in earlier plan, removed)
- ❌ Standalone Search screen (Search is only a bar on Homepage)
- ❌ Contextual Learning Overlay as a distinct feature (was in earlier plan, removed)
- ❌ Market Health Dashboard as a distinct screen (replaced by Affordable & Growing / Popular & Stable tabs on Homepage)
- ❌ Private Market Insights (future roadmap only)

### Features in M4 doc but NOT in IA — need decision

- ⚠️ **Risk Comfort** in onboarding — the M4 writeup describes it, but the IA tree only shows Choose Interest → Confirmation. Either add it to onboarding, or drop it from the M4 description. **Discuss at next meeting.**

---

## What's blocking what

```
M4 (done) ──► M5 implementation
                │
                ├── DECIDE: React Native vs React
                ├── DECIDE: Node.js vs Python
                ├── DECIDE: MVP feature subset (can't build all 9 screens in one semester)
                └── DECIDE: Data source APIs (NewsAPI, Finnhub, etc.)
```

Decisions in CAPS need to happen at the next team meeting before M5 code starts.

---

## Suggested MVP subset for M5

Building all 9 screens to production quality in one semester is unrealistic.
**Proposed MVP cut** (covers the differentiator and the personas):

| Priority | Screen | Why |
|----------|--------|-----|
| P0 | Get Started + Choose Interest + Confirmation | Required, sets up personalization |
| P0 | Homepage (Affordable & Growing + Popular & Stable + Insight section) | The main experience |
| P0 | Event Detail with Event Impact Flow | **THE differentiator** — must work |
| P0 | Company Detail with Confidence Score + Price overview | Required for "research a company" flow |
| P1 | Watchlist (with empty state) | High retention value, simple to build |
| P1 | Settings (basic — Notification + Log Out only) | Required for auth, can ship minimal |
| P2 | Profile screen | Can ship as a stub |
| P2 | Sentiment Pulse 3-tab detail | Can ship with 1 tab first, add others later |
| P2 | "Why This Company" expanded section with Finance chart | Can ship without the chart first |

Lock the cut at the next meeting and update `milestones/milestone-5/TODO.md`.

---

## Weekly cadence

| Day | What |
|-----|------|
| Monday | Team meeting — review TODOs, assign week's tasks |
| Wed/Thu | Async check-in on Discord |
| Friday | Submit week's deliverables, update TODOs |
| Sunday | Prep for Monday, surface blockers |
