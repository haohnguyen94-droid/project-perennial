# `frontend/src/pages/` — TODO

Top-level screen components. **One page per screen in the M4 IA.**

**Owner:** `@jaden` (build), `@cohen` (UX review)

---

## Pages to build (exact 1:1 with the IA)

- [ ] `GetStarted/` — welcome screen
- [ ] `ChooseInterest/` — sector/theme picker
- [ ] `Confirmation/` — review choices, "Update anytime in Settings"
- [ ] `Homepage/` — Search Bar + Affordable & Growing tab + Popular & Stable tab + Insight section
- [ ] `EventDetail/` — What Happened, Effects Markets (Event Impact Flow), Affected Companies, Sentiments, Related Events, Sources tabs
- [ ] `Watchlist/` — list with filter tabs + empty state with topic chips
- [ ] `CompanyDetail/` — Confident Score + Breakdown + Event Exposure + Sentiment + Analyst Outlook + Price breakdown + Sentiment Pulse + Why This Company
- [ ] `Setting/` — Notification, Your Profile (link), Update Preference, Change Password, Log Out
- [ ] `Profile/` — Name, Email, Investment

Auth (not in IA but required):
- [ ] `Login/`
- [ ] `Signup/`

---

## REMOVED from earlier plan (do NOT build)

- ❌ `WeeklyDigest/`
- ❌ `Search/` (standalone search results page — search lives on Homepage)

---

## Each page must

- [ ] Fetch data via hooks from `../hooks/` (no direct fetch inside)
- [ ] Compose components from `../components/`
- [ ] Handle loading / empty / error states
- [ ] Match the Figma low-fi prototype layout closely
- [ ] Flag deviations to `@cohen` before going off-script

---

## Persona check on every page

- Would **Alex** (young pro) find what he needs quickly?
- Would **Maria** (student) understand the language?
- Would **David** (career changer) see the *why* behind every recommendation?

If "no" on any — the page needs work or M2/M4 needs re-reading.
