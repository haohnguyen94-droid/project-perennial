# Perennial

**Investment intelligence for beginners.** Perennial translates global events
into clear, explainable, and actionable investment insights — helping new
investors understand not just what to consider investing in, but **why**.

> A senior project by Team Asian Boiz, California State University Long Beach, Spring 2026.

---

## What Perennial is

A guidance and education layer for beginner investors. It explains **why**
opportunities exist by connecting global events to specific sectors and
companies, with AI-generated confidence scores backed by clear breakdowns.

**Perennial is NOT** a trading platform, brokerage, or budgeting app. We
don't execute orders. We help people understand what's happening and decide
for themselves.

---

## The problem we're solving

Existing investment apps fall into two extremes:

- **Too simple** (e.g. Robinhood) — you can trade, but you get no reasoning
- **Too complex** (e.g. Webull, E*TRADE) — powerful tools, overwhelming for beginners

In between sits a real gap: beginners know that events like tariffs, Fed
decisions, and tech breakthroughs affect markets — but they have no way to
translate that awareness into specific investment decisions.

Perennial fills that gap.

---

## Core features

1. **Affordable & Growing / Popular & Stable** — beginner-friendly company groupings (replaces jargon like "small cap" / "large cap")
2. **Insight / Event Detail** — global events broken down with a visual "How this effects markets" flow tree showing affected sectors and companies. The differentiator.
3. **Company Detail** — Confidence Score (0–100), Score Break Down (tap any factor to learn more), Price Breakdown, Week Range, and three-source Sentiment Pulse (News / Social Media / Analyst)
4. **Why This Company** — Key Reasons + Finance (with "How we analyzed this?" explanations and a 5-year Revenue Growth chart)
5. **Watchlist** — saved companies and sectors with sentiment and score at a glance
6. **Settings** — manage notifications, update preferences, change password
7. **What Interest You + Risk Comfort** — onboarding that personalizes everything downstream

---

## Who it's for

Three primary personas (see `milestones/milestone-2/` for full research):

- **Alex Chen** — Young professional (26), software engineer, follows tech news, wants to translate awareness into action
- **Maria Santos** — College student (20), part-time barista, wants bite-sized guidance and learning embedded in the experience
- **David Park** — Career changer (34), tried apps before, lost money following hype, now wants explainable reasoning

---

## Project structure

```
perennial-project/
├── README.md            ◄── you are here
├── TODO.md              ◄── master TODO with status across all areas
│
├── milestones/          M1–M5 academic deliverables (.docx + presentation files)
├── design/              Wireframes, IA, UI kit, Figma prototype links
├── development/         Frontend, backend, database, shared code
├── docs/                Research, meeting notes, technical specs, API docs
├── assets/              Branding, logos, fonts, marketing material
└── testing/             Unit tests, integration tests, user testing notes
```

**Every major folder has its own `TODO.md`** with a checklist of what goes
there. Start with the root `TODO.md`, then drill down.

---

## Status

| Milestone | Status |
|-----------|--------|
| M1 — Team Charter | ✅ Done |
| M2 — User Research | ✅ Done |
| M3 — Market Research | ✅ Done |
| M4 — Wireframes + IA + Lo-Fi Prototype | ✅ Done (04/27/2026) |
| **M5 — Implementation** | 🔜 Active |

Current focus: see `milestones/milestone-5/TODO.md` and `development/TODO.md`.

---

## Team — Asian Boiz

| Member | Role |
|--------|------|
| Hong Nguyen | Team Leader & Security/Data Privacy Lead |
| Aalind Kale | Backend & System Architecture Lead |
| Cohen Kang | UX & Data Intelligence Lead |
| Jaden Le | Frontend & Integration Lead |
| Bryan Tieu | Market Research & Business Strategy Lead |

---

## Working with the codebase

> ⚠️ M5 implementation hasn't started yet. The folders under `development/`
> exist as placeholders. Setup instructions will live in each folder's README
> once the team locks technology decisions (React Native vs React, Node.js
> vs Python, etc.).

Decisions to lock first — see `development/TODO.md` for the full list.

---

## Communication

- Weekly Zoom/Discord team meeting (Mondays)
- Async messaging in Discord (24-hour response expectation)
- Internal deadlines set 48 hours before course deadlines
- Meeting notes filed in `docs/meeting-notes/` after every session

---

## Design principles

These guide every feature decision:

1. **Clarity over density** — every screen understandable in 5 seconds
2. **Explain, don't assume** — every metric includes a "why"
3. **Progressive disclosure** — summaries first, details on tap
4. **Traffic-light simplicity** — green/yellow/red instead of complex charts
5. **Beginner language over jargon** — "Affordable & Growing" not "small cap"

---

## Out of scope (intentionally)

We've explicitly chosen NOT to build:

- Trading / order execution (we're not a brokerage)
- Budgeting features (we pivoted away from that)
- Advanced charts / candlesticks / technical indicators
- Portfolio tracking and allocation visualization
- Standalone Weekly Digest
- Private market access in MVP (future roadmap)

Push back if any of these creep back in during development.

---

## License & data handling

All research participant data is handled per CCPA and GDPR principles.
Consent forms and transcripts are stored in `docs/research/` with PII
redacted from public-facing artifacts.

This project is academic in nature; no commercial license has been issued.
