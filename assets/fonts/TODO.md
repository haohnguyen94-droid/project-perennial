# `assets/fonts/` — TODO

Font files, only if not loading from a CDN.

**Owner:** `@cohen`

---

## Decisions

- [ ] Pick font: Inter or SF Pro Display (per DESIGN_SYSTEM.md)
- [ ] CDN vs self-host
  - **CDN (recommended):** faster setup, no license files
  - **Self-host:** full control, slightly faster after first load

---

## If self-hosting

- [ ] Download only the weights you use
- [ ] Include both `.woff2` and `.woff`
- [ ] Include `LICENSE.txt` if required
- [ ] Document the choice in `../../docs/DECISIONS.md`

---

## Suggested weights

If Inter:
- [ ] Regular 400
- [ ] Medium 500
- [ ] SemiBold 600
- [ ] Bold 700

Don't load all 9 weights.
