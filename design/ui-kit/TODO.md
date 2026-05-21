# `design/ui-kit/` — TODO

Design tokens, component specs, shared UI patterns.

**Owner:** `@cohen`

---

## Status

- [x] `DESIGN_SYSTEM.md` — colors, typography, principles drafted
- [ ] Figma component library matching DESIGN_SYSTEM.md
- [ ] Component specs documented

---

## Files in this folder

- [x] `DESIGN_SYSTEM.md` — already exists; keep updated
- [ ] `COMPONENTS.md` — spec for each reusable component
- [ ] `figma-link.md` — link to the Figma component library file

---

## Components to design in Figma (matched to the M4 prototype)

Build each component **once**, reuse everywhere. Each needs default, hover/active, disabled states where applicable.

### Score / sentiment / data display
- [ ] **Confident Score Badge** — 0–100, color-coded (0–39 red, 40–69 yellow/mixed, 70–100 green), traffic-light dot
- [ ] **Sentiment Pulse** — 3 tabs (News / Social Media / Analyst), each with its own pos/mixed/neg breakdown bar
- [ ] **Sentiment indicator pill** — small positive/mixed/negative tag for use in lists
- [ ] **Traffic-light dot** — green/yellow/red dot used in Affordable & Growing rows

### Price / company data display
- [ ] **Price Overview block** — current price, fair value range, "In range" indicator
- [ ] **52-Week Range bar** — visual bar with low / average / current / high markers
- [ ] **Revenue Growth chart** — 5-year line/bar chart (simple, no candlesticks)

### Event / Insight components
- [ ] **Event Card (collapsed)** — headline, brief impact summary, expand control
- [ ] **Event Impact Flow chart** — THE differentiator. Visual mapping of event → affected sectors → companies (positive + negative branches). Spec this carefully.
- [ ] **Affected Company Row** — name, sector tag, sentiment indicator, current price, "+ Watchlist" button
- [ ] **Related Events list** — compact list of other relevant events
- [ ] **Public Sentiment bar (event-level)** — bar showing overall sentiment with source breakdown

### Homepage organization
- [ ] **Tab pair: "Affordable & Growing" / "Popular & Stable"** — toggle between two views of company listings
- [ ] **Company row (in tab)** — ticker, traffic-light dot, momentum arrow (↑ ↓ →), current price

### Watchlist components
- [ ] **Filter tab group: "All / Companies / Sectors"** — top-of-watchlist filter
- [ ] **Watchlist row** — name, sector tag, sentiment indicator, Confident Score (colored), price, View/Remove actions
- [ ] **Watchlist empty state** — friendly prompt + topic chips (AI, Crypto, Green Energy, Finance)
- [ ] **"New Event" badge** — red dot on watchlist items with recent activity

### Form / input
- [ ] **Button variants** — primary, secondary, ghost, destructive
- [ ] **TextInput / Search Bar**
- [ ] **Toggle** — for Settings notification preferences
- [ ] **Interest chips** — multi-select chips for Choose Interest screen

### Layout / navigation
- [ ] **Left sidebar nav** — used on desktop/wide views (Insight / Watchlist / Setting / Profile)
- [ ] **Header / top bar** — with search bar on Homepage
- [ ] **Card surface** — generic rounded card with shadow used everywhere
- [ ] **Section header** — for "What Happened", "How This Affects Markets", etc.

### Feedback / state
- [ ] **Loading** — skeleton or spinner
- [ ] **Empty state** — generic empty placeholder (Watchlist has a custom one)
- [ ] **Error state** — generic error with retry
- [ ] **Disclaimer line** — "AI-generated guidance, not financial advice" footer

---

## Open decisions

- [ ] Confirm typography — Inter vs SF Pro Display
- [ ] Pick exact icon set (Heroicons, Phosphor, Lucide, custom?)
- [ ] Decide whether to support dark mode in MVP or later
- [ ] Confirm left sidebar nav vs bottom tab bar for mobile (IA shows top-level entry points but not nav layout)
