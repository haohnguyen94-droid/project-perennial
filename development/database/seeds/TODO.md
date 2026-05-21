# `database/seeds/` — TODO

Fake data for local dev and testing. Should produce a Homepage that looks
populated and an Event Detail with a believable Event Impact Flow.

**Owner:** `@aalind` (infra), `@bryan` (realistic content)

---

## Seeds to create

- [ ] **3 sample users** matching personas (Alex, Maria, David) with completed onboarding
- [ ] **~50 companies** distributed across sectors (Tech, Energy, Healthcare, Finance, Crypto/Web3)
- [ ] Each company gets:
  - Traffic-light + momentum status
  - Current price + 52-week range
  - Fair value range
  - 5-year revenue rows
  - A current Confident Score with Breakdown
  - Sentiment Pulse data for all 3 source types
  - A Why This Company entry with key reasons
- [ ] **~20 events** across sectors with believable headlines
- [ ] Each event gets:
  - What Happened + Effects Markets summaries
  - Sector impacts (positive/negative branches)
  - Company impacts feeding into the Event Impact Flow
  - 2–3 sources per type (news / social / analyst)
- [ ] **Sample watchlists** — each user has 3–5 companies + 1 sector watched

---

## Files

- [ ] `seed.{js,ts,py}` — runs all seeds in order
- [ ] `users.json`
- [ ] `companies.json`
- [ ] `events.json`
- [ ] `event-impacts.json` — the Event Impact Flow data

---

## Conventions

- [ ] Idempotent — running twice doesn't duplicate
- [ ] Triggered by `npm run db:reset` or equivalent
- [ ] Use plausible-but-fake company names where appropriate
- [ ] Never seed real user data
