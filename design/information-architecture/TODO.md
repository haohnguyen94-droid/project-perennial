# `design/information-architecture/` — TODO

The Information Architecture diagram is the **locked source of truth** for
what screens exist in Perennial.

**Owner:** `@cohen` (built the IA in Figma)

---

## Status

- [x] IA diagram built in Figma
- [x] All 9 top-level screens defined
- [x] Sub-sections of Event Detail and Company Detail defined
- [ ] Export IA as PNG/PDF to this folder
- [ ] Add Figma link to `IA_LINK.md` in this folder

---

## Files this folder should contain

- [ ] `information-architecture.png` — exported diagram
- [ ] `information-architecture.pdf` — print-ready version
- [ ] `IA_LINK.md` — Figma file link + access notes

---

## The locked screen list (from the IA)

> **If a screen is not in this list, it is not being built in M5.**
> Adding a screen requires team approval.

```
Get Started
└── Choose Interest
    └── Confirmation
        └── Homepage
            ├── Search Bar
            ├── Affordable and Growing
            ├── Popular and Stable
            ├── Insight
            │   └── Event Detail
            │       ├── What Happened
            │       ├── Effects Markets
            │       ├── Affected Companies → Company Detail
            │       ├── Sentiments
            │       ├── Related Events
            │       └── Sources
            │           ├── News
            │           ├── Social Media
            │           └── Analyst
            ├── Watchlist
            │   ├── Watchlist list
            │   └── Empty State
            ├── Setting
            │   ├── Notification
            │   ├── Your Profile
            │   ├── Update Preference
            │   ├── Change Your Password
            │   └── Log Out
            └── Profile
                ├── Name
                ├── Email
                └── Investment

Company Detail (reachable from Affordable & Growing / Popular & Stable /
                                Affected Companies / Watchlist)
├── Confident Score
├── Breakdown
├── Event Exposure
├── Sentiment
├── Analyst Outlook
├── Price break down
├── Sentiment Pulse
│   ├── News
│   ├── Social Media
│   └── Analyst
└── Why This Company
    ├── Key Reasons
    └── Finance
```

---

## Notes for engineering

- The Search Bar is a Homepage component, **not a separate screen**
- Profile and Setting are **separate screens**, not nested under Setting
- Sentiment Pulse on Company Detail has 3 sub-tabs (News / Social Media / Analyst)
- "Why This Company" expands to show Key Reasons + Finance sections
- Company Detail is reachable from multiple places — Affordable & Growing rows, Popular & Stable rows, Affected Companies in Event Detail, and Watchlist
