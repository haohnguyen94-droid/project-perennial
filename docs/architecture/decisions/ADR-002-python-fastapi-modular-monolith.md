# ADR-002 — Python backend: FastAPI modular monolith, two entrypoints

**Status:** Accepted (language: team answer 2026-08-03; framework: architect recommendation) · **Deciders:** @aalind lead

## Context

`development/TODO.md` framed "Node.js vs Python" as open ("Python likely better for AI/ML, Node likely faster to ship"). Meanwhile ~1,500 lines of working **Python** already exist on `origin/cohen-working` (YouTube transcript pipeline) and `origin/hong-working` (FMP/ARK/insider fetchers). The backend has two jobs with very different shapes: serving IA-aligned REST reads/writes, and running an hourly content pipeline.

## Options

1. **Single Python codebase (FastAPI), two processes** — API server + scheduled pipeline sharing models/DB.
2. Node/Express API + Python pipeline as separate services — two languages, two toolchains, an inter-service contract for a 5-person team.
3. Python everywhere but split into microservices — deployment and versioning overhead with no load to justify it (Q4: demo scale).
4. Django instead of FastAPI — viable; evaluated as Stack B in [stack-decision.md](../stack-decision.md).

## Decision

**Option 1.** One repo module `backend/` containing `api/` (routers), `services/`, `models/`, `middleware/`, `clients/`, `pipeline/` — matching the layer plan already written in `development/backend/*/TODO.md`. Entrypoints: `uvicorn app.main:app` and `python -m pipeline.run`. Framework: **FastAPI** (Pydantic validation the backend TODO requires, OpenAPI generation that replaces `shared/types`, async httpx for the pipeline).

## Consequences

- Cohen's and Hao's code is **absorbed, not rewritten**: fetchers move under `pipeline/fetchers/`, file/Firestore writes become SQLAlchemy upserts (their own comments anticipate this).
- The existing misplacements get corrected in the move (`youtube.py` currently sits in `src/api/`, `firestore_upload.py` in `src/middleware/` on `cohen-working` — both violate the folder contracts in `backend/src/api/TODO.md` / `middleware/TODO.md`).
- `development/shared/types/` is retired in favor of an OpenAPI-generated TS client (ADR-010), exactly as `development/shared/TODO.md` predicted for a Python backend.
- One language for the whole backend team; Node exists nowhere in the stack.
- Trade-off accepted: FastAPI means hand-assembling auth/admin conveniences — argued honestly in [stack-decision.md](../stack-decision.md) ("case against my own pick").
