# ADR-009 — Data source per need (one primary each, seams for failover)

**Status:** Accepted with one open pick (news provider) · **Deciders:** @aalind, @cohen, @hong

## Context

`docs/technical-specs/TODO.md` wants a `DATA_SOURCES.md` naming a financial API, news API, three sentiment sources, rate limits, and failover. `backend/src/utils/TODO.md` sketches clients for Alpha Vantage/Finnhub/Polygon, NewsAPI/GNews, Reddit, StockTwits, and an unnamed "analyst feed" — while the actually-working code uses FMP, arkfunds.io, SecuritiesDB, Senate Stock Watcher, and YouTube. The lists disagree; this ADR reconciles them around what exists and what each screen needs.

## Decision — source per product need

| Product need | Source | Status | Constraint |
|---|---|---|---|
| Quotes, market cap, 52-wk, 5-yr revenue | **FMP** | Key provisioned (`.env.example` on `hong-working`) | Free tier 250 req/day → batch endpoints, daily fundamentals (ADR-004) |
| Congress trades (consensus signal) | **FMP + Senate Stock Watcher** | Working (`fmp.py`) | 3 pages/chamber/day |
| Growth-stock signal | **arkfunds.io** | Working (`ark.py`) | No key; daily |
| Insider buys | **SecuritiesDB** | Working (`insider.py`) | No key; 0.5 s spacing |
| **Analyst** pulse tab + Analyst Outlook | **Finnhub** recommendation trends + price targets | Key provisioned, client to build | Free tier ~60 calls/min — ample. *Resolves the "analyst-feed" placeholder — previously pointed at nothing* |
| News events | **NewsAPI or GNews — pick at next meeting** after verifying current free-tier terms (both ~100 req/day; NewsAPI free is dev-only-licensed, GNews allows more) | To build | Budgeted hourly fetch |
| **Social** pulse tab | **YouTube transcripts** (Cohen's pipeline) | Working (`cohen-working`) | See risk note below |
| LLM | **Anthropic Claude Sonnet** | ADR-005 | Budget alarm $2/day |

Dropped from the earlier sketch: **Reddit and StockTwits clients** (`utils/TODO.md`) — three social sources is scope creep when one works today; the Twitter bearer token in `.env.example` is likewise parked. The per-source client interface keeps any of them addable later without refactor (that interface *is* the failover plan at this scale — a second provider is a second implementation behind the same protocol).

## Risk note — YouTube via yt-dlp (accepted risk, revisit if it bites)

Transcript scraping via yt-dlp sits in a gray area of YouTube's ToS. Accepted for an academic, non-commercial project (`README.md`: "no commercial license has been issued"), with mitigations: cache transcripts (never refetch), respect backoff (the code already does), and a graceful degrade path — Sentiment Pulse ships tabs incrementally, so News+Analyst alone still demos (build-plan risk #5). If the team is uncomfortable, the swap is Reddit's official API as the social source; the client interface makes that a bounded task.

## Consequences

- `DATA_SOURCES.md` in `docs/technical-specs/` can now be written by copying this table and adding observed rate-limit numbers once the clients run.
- Every client enforces its own daily budget from a shared budget table; exhaustion marks the stage `partial`, never crashes the run.
