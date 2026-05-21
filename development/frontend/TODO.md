# `development/frontend/` — TODO

User-facing app.

**Owner:** `@jaden`

---

## Setup

- [ ] Decide React Native (mobile) vs React (web)
- [ ] Initialize project
- [ ] Set up TypeScript
- [ ] Set up linter + formatter
- [ ] Set up routing (React Router for web, Expo Router for RN)
- [ ] Set up state management (React Query + Context to start; add Zustand later if needed)
- [ ] Set up styling (Tailwind, styled-components, or CSS Modules)
- [ ] Set up theme provider using colors from `../../design/ui-kit/DESIGN_SYSTEM.md`
- [ ] Add `README.md` explaining how to run frontend locally
- [ ] Configure API base URL via env var

---

## Folder map (under `src/`)

| Folder | TODO |
|--------|------|
| `components/` | [TODO](src/components/TODO.md) |
| `pages/` | [TODO](src/pages/TODO.md) |
| `hooks/` | [TODO](src/hooks/TODO.md) |
| `styles/` | [TODO](src/styles/TODO.md) |
| `utils/` | [TODO](src/utils/TODO.md) |

Plus:

| Folder | TODO |
|--------|------|
| `public/` | [TODO](public/TODO.md) |
| `assets/` | [TODO](assets/TODO.md) |

---

## Build order

1. Theme + design tokens → `src/styles/TODO.md`
2. Reusable components → `src/components/TODO.md` (build Event Impact Flow component first — it's the hardest + the differentiator)
3. Pages built from components → `src/pages/TODO.md`
4. Connect to API via hooks → `src/hooks/TODO.md`
5. Polish — empty states, loading, errors
