# `shared/config/` — TODO

Constants used by both FE and BE.

**Owner:** `@aalind`

---

## Things that go here

- [ ] `sectors.ts` — canonical sector list (Tech, Energy, Healthcare, Finance, Crypto, etc.)
- [ ] `confident-score-bands.ts` — 0–39 red, 40–69 mixed, 70–100 green thresholds
- [ ] `traffic-light.ts` — display labels + colors
- [ ] `sentiment-sources.ts` — canonical list (news, social_media, analyst)
- [ ] `watchlist-topic-chips.ts` — AI, Crypto, Green Energy, Finance (for the empty state)
- [ ] `api-routes.ts` — string constants for every API path

---

## What does NOT go here

- ❌ Secrets / API keys / env-specific URLs — those are env vars
- ❌ Anything that differs between FE and BE
- ❌ Anything that needs to be runtime-configurable
