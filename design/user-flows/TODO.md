# `design/user-flows/` — TODO

Diagrams showing how users move between screens.

**Owner:** `@jaden`

---

## Status

- [x] `USER_FLOWS.md` — text-based flows drafted
- [ ] Updated to match the M4 IA (some flows no longer apply)

---

## Active flows (match IA)

These flows are what M5 must support:

### Flow 1 — First-time onboarding
```
Get Started → Choose Interest → Confirmation → Homepage
```

### Flow 2 — Discover investment via event (Use Case 1)
```
Homepage → Insight section → Event Detail
  → What Happened → Effects Markets (Event Impact Flow chart)
  → Affected Companies → tap company → Company Detail
  → "+ Watchlist"
```

### Flow 3 — Research a company (Use Case 2)
```
Homepage → Search Bar (or Affordable & Growing / Popular & Stable row)
  → Company Detail
  → View Confident Score + Price Overview
  → Tap Sentiment Pulse tabs (News / Social / Analyst)
  → Tap "Why This Company" → Key Reasons + Finance
  → "+ Watchlist"
```

### Flow 4 — Manage Watchlist
```
Homepage → Watchlist
  → Filter by All / Companies / Sectors
  → tap row → View Company Detail
  → Remove items
(Empty state: shows topic chips → tap a chip → Homepage Insight section)
```

### Flow 5 — Settings & Profile
```
Homepage → Setting → Notification / Update Preference / Change Password / Log Out
Homepage → Profile → Name / Email / Investment
```

---

## REMOVED flows (no longer in scope per M4)

- ❌ Weekly Digest flow — Weekly Digest screen rejected
- ❌ Privacy & Data Management flow (Use Case 4 detailed version) — simplified to basic Settings only
- ❌ Daily check flow with separate alerts page — alerts now show as "New Event" badges on Watchlist items

---

## Visual flow diagrams to create

- [ ] `flow-01-onboarding.png`
- [ ] `flow-02-discover-event.png` ← most important, shows differentiator
- [ ] `flow-03-research-company.png`
- [ ] `flow-04-watchlist.png`
- [ ] `flow-05-settings-profile.png`

Use Figma / FigJam / Miro. Export PNGs to this folder.
