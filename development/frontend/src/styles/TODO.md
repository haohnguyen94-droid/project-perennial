# `frontend/src/styles/` — TODO

Global styles, theme, design tokens.

**Owner:** `@jaden`

---

## Files

- [ ] `theme.{ts,js}` — colors, typography, spacing as JS constants
- [ ] `globals.css` — base styles, font import, body reset
- [ ] `tokens.{ts,js}` — semantic tokens (`colors.primary`, `colors.danger`)

---

## Colors (from DESIGN_SYSTEM.md)

```
primary: {
  dark:  '#1B4332',
  base:  '#2D6A4F',
  light: '#40916C',
  accent: '#52B788',
}
background: '#F8F9FA'
surface:    '#FFFFFF'
text: {
  primary:   '#1A1A2E',
  secondary: '#6C757D',
}
status: {
  danger:  '#DC3545',  // negative sentiment, low Confident Score
  warning: '#FFC107',  // mixed sentiment, mid Confident Score
  success: '#28A745',  // positive sentiment, high Confident Score
}
```

---

## Typography
- [ ] Import Inter or SF Pro (decide first)
- [ ] Define heading sizes (h1–h4)
- [ ] Define body sizes (regular + small)
- [ ] Tabular figures for financial numbers

---

## Conventions

- [ ] **Never hardcode hex** — always theme tokens
- [ ] Components reference semantic tokens (`colors.status.success`), not raw colors
