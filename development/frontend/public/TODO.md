# `frontend/public/` — TODO

Static files served as-is at the root of the deployed app.

**Owner:** `@jaden`

---

## Files to add

- [ ] `favicon.ico` (16x16 + 32x32)
- [ ] `favicon.svg`
- [ ] `apple-touch-icon.png` (180x180)
- [ ] `manifest.json` (PWA)
- [ ] `robots.txt`
- [ ] (optional) `og-image.png` (1200x630 social share preview)

---

## Rules

- Files referenced by absolute path: `/favicon.ico`
- Don't put in-app images here — those go in `../src/assets/` so they get bundled
- Source assets (logo SVGs etc.) live in `../../../assets/branding/` — copy exports here
