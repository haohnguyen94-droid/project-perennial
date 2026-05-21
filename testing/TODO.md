# `testing/` — TODO

All testing.

**Primary owners:** `@all`

---

## Folder map

| Folder | TODO |
|--------|------|
| `unit/` | [TODO](unit/TODO.md) |
| `integration/` | [TODO](integration/TODO.md) |
| `user-testing/` | [TODO](user-testing/TODO.md) |

---

## What's tested where

| Thing | Where |
|-------|-------|
| `scoreToColor(72)` returns green | `unit/` |
| `ConfidentScoreBadge` renders correctly | `unit/` |
| `EventImpactFlow` renders the right branches given mock data | `unit/` |
| `POST /api/user/watchlist` writes to DB | `integration/` |
| Real user (Maria persona) can add a company to watchlist | `user-testing/` |

---

## Rules

- Every backend service has unit tests
- Every API endpoint has at least one integration test (happy + error)
- Every reusable component has a render test
- User testing happens during M5 once the prototype is clickable
- Tests run in CI before merge

---

## Order

1. Unit test framework
2. Integration test framework
3. Write tests **as you write code**, not after
4. User testing happens once a working prototype exists
