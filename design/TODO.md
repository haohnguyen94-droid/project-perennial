# `design/` — TODO

All design work for Perennial.
M4 is **done** — wireframes, IA, and a low-fidelity Figma prototype exist.
M5 design work is mostly **maintenance + minor refinement**, not net new design.

**Primary owners:** `@cohen @jaden`

---

## Folder map

| Subfolder | Status | Purpose | TODO |
|-----------|--------|---------|------|
| `information-architecture/` | ✅ Done in Figma | The locked IA tree | [TODO](information-architecture/TODO.md) |
| `wireframes/` | ✅ Done | Paper sketches + low-fi Figma | [TODO](wireframes/TODO.md) |
| `ui-kit/` | 🔜 Partial | Design tokens, components | [TODO](ui-kit/TODO.md) |
| `user-flows/` | ✅ Done (USER_FLOWS.md) | How users move between screens | [TODO](user-flows/TODO.md) |
| `prototypes/` | ✅ Lo-fi done | Figma prototype links | [TODO](prototypes/TODO.md) |
| `mockups/` | ⏳ Optional | High-fidelity polish (only if time) | [TODO](mockups/TODO.md) |

---

## What's done after M4

- ✅ Information Architecture finalized in Figma
- ✅ Paper wireframes from Hong, Aalind, Jaden (in Drive)
- ✅ Final lo-fi wireframes in Figma
- ✅ Interactive Figma prototype (low-fidelity) wired up

---

## What still needs design work in M5

- [ ] Build Figma component library matching DESIGN_SYSTEM.md (so devs have a clean spec)
- [ ] Spec each unique component used in the prototype (props, states, sizes)
- [ ] Decide on icon set (Heroicons / Lucide / Phosphor / custom)
- [ ] Confirm typography choice (Inter vs SF Pro)
- [ ] Refine the **Event Impact Flow** visual — it's the differentiator; design must be unambiguous for engineers to implement
- [ ] (Optional) High-fidelity mockup of Homepage and Event Detail for marketing material

---

## Design principles (from DESIGN_SYSTEM.md — apply everywhere)

1. **Clarity over density** — every screen understandable in 5 seconds
2. **Explain, don't assume** — every metric includes a "why"
3. **Progressive disclosure** — summaries first, details on tap
4. **Traffic-light simplicity** — green/yellow/red color coding
5. **Beginner language over jargon** — "Affordable & Growing" not "small cap"

---

## Persona alignment check

Every screen and component should serve at least one persona well:
- **Alex** (young pro, 26) — quick scanning, tech news → investment translation
- **Maria** (student, 20) — bite-sized info, plain language, no jargon
- **David** (career changer, 34) — trust through transparency, "why" behind every score

If a screen doesn't serve any persona, it shouldn't be in M5.
