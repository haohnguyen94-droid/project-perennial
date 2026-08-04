# Perennial — Stack Decision

**Status:** Recommended (Phase 3 deliverable) · **Date:** 2026-08-03
**Frame:** Team answers already lock *Python backend, PostgreSQL, React web app* (overview.md). Those are not re-litigated here. What remains genuinely open — and where real, viable alternatives exist — is **how much backend we hand-write vs buy**, which framework philosophy, and where it runs. The three stacks below differ materially on exactly that axis. None is a strawman; each has a real constituency and would ship this product.

---

## The three candidate stacks

### Stack A — "Boring Python monolith" (FastAPI + owned auth)

| Layer | Choice |
|---|---|
| Language/framework | Python 3.12 · **FastAPI** · SQLAlchemy 2.0 · Alembic |
| Datastore | Railway managed **PostgreSQL 16** |
| Async layer | **None** — Railway cron → `python -m pipeline.run`; in-run concurrency via `asyncio` + `httpx`; no queue, no Redis (ADR-007) |
| Hosting | Railway (API + cron + Postgres) · Vercel (React SPA) |
| Load-bearing libraries | `pydantic` v2 (+`pydantic-settings`), `httpx`, `tenacity`, `anthropic` (Sonnet: `claude-sonnet-5`), `argon2-cffi`, `PyJWT`, `structlog`, `pytest` · Frontend: Vite, TypeScript, React Router, TanStack Query, Tailwind, Recharts, `openapi-typescript` (generated client, ADR-010) |

Everything is explicit and hand-assembled: auth, CRUD, admin tasks (via CLI). FastAPI's OpenAPI generation replaces the `shared/types` folder (`development/shared/TODO.md` itself says: "If backend is Python … you keep an OpenAPI spec instead").

### Stack B — "Batteries + admin" (Django)

| Layer | Choice |
|---|---|
| Language/framework | Python 3.12 · **Django 5 + Django REST Framework** · Django ORM/migrations |
| Datastore | Same managed Postgres |
| Async layer | Same cron-driven pipeline (Django management commands); no Celery at this scale |
| Hosting | Same Railway + Vercel |
| Load-bearing libraries | DRF, `django-allauth`/built-in auth (argon2 hasher), `drf-spectacular` (OpenAPI), same `anthropic`/`httpx`/`tenacity`; same frontend |

The pitch is not "Django is nicer" — it's the **Django admin**: a free, built-in content-curation UI. Perennial is a *content product*; before the pipeline is trustworthy, someone will hand-fix a bad impact-flow branch, retire a mangled event, and tune seed data (`database/seeds/TODO.md` wants "a believable Event Impact Flow"). In Stack A that's psql or throwaway scripts; in Stack B it's a form a non-backend teammate (Bryan, Cohen) can use.

### Stack C — "BaaS-lean" (Supabase + pipeline-only Python)

| Layer | Choice |
|---|---|
| Backend | **Supabase** (managed Postgres + Auth + auto-generated REST/PostgREST + Row Level Security) — most of `backend/src/api` is *not written at all* |
| Custom code | Python **pipeline only** (the LLM/ingestion work), run as Railway cron or GitHub Actions schedule, writing to Supabase Postgres via service key; a handful of Supabase Edge Functions for the few endpoints RLS can't express (bulk watchlist-add, data export) |
| Hosting | Supabase free tier + Vercel + one tiny cron worker |
| Load-bearing libraries | `supabase-js` (frontend), same Python pipeline libs |

The pitch: the team's differentiating work is the pipeline and the EventImpactFlow UI — Stack C deletes ~40% of the planned backend surface (auth routes, CRUD routes, JWT middleware) and spends that time on the differentiator.

---

## Comparison

| Criterion | A — FastAPI monolith | B — Django | C — Supabase-lean |
|---|---|---|---|
| **Fit to these specific requirements** (thin-handler convention, explainable content pipeline, IA-shaped REST) | **High.** Matches the repo's own folder plan (`api/services/models/middleware/utils`) almost 1:1; pipeline and API share models naturally | High for API; admin is a bonus the requirements never asked for; Django's app structure fights the repo's planned layout a little | **Medium.** Pipeline fits fine; but composed endpoints (`/api/homepage` bundle, event detail tree) fight PostgREST — you end up writing Postgres views/functions or Edge Functions, relocating complexity rather than removing it |
| **Time to first working version** (walking skeleton) | Medium — auth + scaffolding is ~1–2 weeks of the schedule | Medium — batteries help, DRF boilerplate gives some back | **Fastest** — auth is a checkbox; CRUD is free; skeleton = pipeline + UI only |
| **Operational burden** | Low: 2 deploys + managed PG | Low (same shape) | **Lowest** day-to-day; *but* two control planes (Supabase + worker host) and RLS policies become your security-critical code |
| **Cost at current scale** | ~$5–10/mo + LLM (~$10–30/mo with batch+hash gating) | Same | ~$0–5/mo + LLM (Supabase free tier covers demo scale) |
| **Cost at 10× scale** (~1k users — still tiny) | ~$20–40/mo; nothing changes structurally | Same | Supabase Pro $25/mo; still fine |
| **Scaling ceiling** (beyond any stated need — designed for demo scale per Q4) | High: stateless API scales horizontally; pipeline is the eventual bottleneck and shards by ticker | Same | Medium-high; RLS-heavy PostgREST gets hard to evolve; ceiling is architectural (query shape), not load |
| **Ecosystem maturity** | Very high (FastAPI is the default Python API stack in 2026) | Highest (20+ yrs) | High but fastest-moving; RLS patterns have sharp edges |
| **Hiring / learning curve for THIS team** | Team already writes Python (both working branches are Python); FastAPI is the smallest step. Jaden learns only the frontend half | Django is a bigger framework to learn than the problem needs | Least backend to learn; **but** RLS + Postgres functions is a genuinely different skill, and it's nobody's stated skill |
| **Lock-in** | Minimal — plain Python + plain Postgres; `pg_dump` walks away | Minimal (ORM migration cost only) | **Real but bounded**: data walks away (it's Postgres), but auth users, RLS policies, and Edge Functions are Supabase-shaped rewrites |
| **Team-goal fit (academic)** | Hong builds auth (their stated lead area); Aalind builds real architecture — strong M5 writeup material | Similar, minus some auth depth | **Weak for Hong**: auth outsourced to a checkbox undercuts the Security/Data-Privacy Lead role from `README.md` |

---

## Recommendation: Stack A — the boring FastAPI monolith

For *this* team, *this* semester, *this* repo:

1. **It matches the plan the team already wrote.** The TODO tree under `development/backend/` — thin handlers, framework-agnostic services, models, middleware list — *is* a FastAPI monolith described without naming it. Adopting A means executing the existing plan, not renegotiating it.
2. **It absorbs the existing code with the least friction.** Cohen's and Hao's pipelines are plain Python scripts; they become pipeline stages by swapping file/Firestore writes for SQLAlchemy upserts. No framework has to agree with them.
3. **Every skill practiced is the plainest, most transferable version** — for a senior project that is a feature: the M5 writeup ("architecture, decisions, tradeoffs" per `milestones/milestone-5/TODO.md`) is easier to tell about a system you assembled than one you configured.
4. **The team roles map cleanly** — Hong: auth service + middleware; Aalind: schema, API, pipeline skeleton; Cohen: LLM stages + sentiment; Jaden: SPA; Bryan: seed content, eval set, docs.

### The strongest case AGAINST my own pick

- **You will hand-write everything Supabase gives away, and auth is the most dangerous thing a student team can hand-write.** Token rotation, revocation, password reset, timing-safe comparisons — each has a well-known footgun, and a demo-day auth bug is mortifying in exactly the way a missing feature is not. Stack C makes that class of bug nearly impossible and would land the walking skeleton one to two weeks sooner — on a five-month clock, that's material.
- **Stack A has no content-curation story.** The first month of pipeline output will contain embarrassing impact flows. In A, fixing them means a teammate with psql; in B it's an admin form anyone can use. There's a real chance you end up hand-building a crappy admin page anyway — which is Django admin with extra steps.
- **"Boring assembly" burns decision budget.** FastAPI makes you choose (project layout, auth wiring, settings, test fixtures) where Django/Supabase decide for you. A five-person team with one backend lead can lose weeks to choices B and C never surface.

I hold the recommendation despite this because the team's answers (Python, Postgres, own the backend) and the org chart (Hong owns auth *as a learning goal*) point at A — but the counter-case is real, not decorative.

### What fact would flip the recommendation

- **If the team says backend labor must be minimized to protect the differentiator** (or the walking skeleton slips >3 weeks) → flip to **C**. The moment shipping the EventImpactFlow matters more than owning auth, C dominates.
- **If hand-curating content becomes a weekly activity** (pipeline quality lower than hoped, demo polish depends on manual fixes) → flip to **B** for the admin.
- **If Jaden's React footing turns out weaker than assumed** → doesn't flip the backend, but flips the frontend toward heavier scaffolding (Next.js on Vercel) — orthogonal to A/B/C.

---

## Reversibility ledger — where to spend rigor

**Cheap to reverse later (decide fast, don't over-deliberate):**

| Decision | Reversal cost |
|---|---|
| Hosting platform (Railway ↔ Render ↔ Fly) | Hours — 12-factor config |
| Scheduler (cron ↔ APScheduler ↔ Celery later) | Hours — pipeline is a plain callable |
| News provider (NewsAPI ↔ GNews) | One client module (ADR-009 keeps a per-source interface) |
| LLM model choice within Anthropic (Sonnet ↔ Haiku for sub-tasks) | A config string + eval re-run |
| Styling (Tailwind ↔ CSS Modules), charting lib, icon set | Component-local |
| Adding Redis / staging env / Sentry | Additive, no rework |

**Effectively permanent (spend the rigor here):**

| Decision | Why it hardens |
|---|---|
| **Relational schema shape** (data-flows.md §1) — especially events→impacts→explanations provenance | Every feature, seed file, and test builds on it; renaming/splitting tables after content exists is the classic rewrite trigger |
| **REST contract** (paths + response shapes from `backend/TODO.md`) | Frontend, tests, and docs all couple to it; version it from day one (`/api` = v1 implicit) |
| **Bucket semantics** (ADR-008) | It's the product's public vocabulary — marketing (`assets/marketing/TODO.md`) already leads with it; changing meaning after user testing invalidates research |
| **Python as the backend language** | Rewrite-sized by definition |
| **LLM-at-ingest (never in request path)** (ADR-005) | The cost model, latency budget, schema (`content_hash` gates), and failure story all assume it |
| **Explainability invariant** (every number ships with its explanation string) | Baked into schema columns and API shapes; retrofitting explanations onto opaque numbers is a redesign, not a patch |

**Where boring, proven tech beats the interesting option — explicitly:**

- **REST over GraphQL.** Nine fixed screens with server-composed bundles is REST's home turf; GraphQL's flexibility solves a problem this product doesn't have and adds a resolver layer to secure.
- **cron + Postgres over Celery/Redis/Kafka.** One hourly job. A queue would be résumé-driven engineering (ADR-007).
- **Postgres full-text/ILIKE over a search engine.** 150 tickers. Nothing to elaborate.
- **Server-computed JSON over websockets/SSE.** Hourly data cannot justify a live channel.
- **A deterministic score formula (code) over "let the LLM score it."** Reproducible, testable (`unit/TODO.md` expects `confident-score.test` with expected scores), and cheap; the LLM only *explains*. The interesting option (LLM-as-scorer) is unauditable and was rejected deliberately.
- **JWT + argon2 with a library over a novel session scheme** — and if the team ever wavers on owning auth at all, the boring answer is Clerk/Supabase, not cleverness.
