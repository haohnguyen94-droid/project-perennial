# ADR-010 — REST + OpenAPI-generated TypeScript client (retire `shared/types/`)

**Status:** Accepted (architect recommendation) · **Deciders:** @aalind, @jaden

## Context

`development/shared/types/TODO.md` plans a hand-maintained shared TypeScript types folder — but `development/shared/TODO.md` itself flags: "Only useful if both FE and BE use TypeScript. If backend is Python … you keep an OpenAPI spec instead." ADR-002 made the backend Python.

## Options

1. **Generate:** FastAPI emits OpenAPI for free; `openapi-typescript` generates the response/request types the frontend hooks consume; CI regenerates and fails on drift.
2. Hand-maintain parallel Pydantic + TS types — guaranteed drift, the exact failure `shared/` existed to prevent.
3. GraphQL for typed contracts — a schema layer and resolver security surface for nine fixed screens; rejected in [stack-decision.md](../stack-decision.md) ("boring beats interesting").

## Decision

**Option 1.** The Pydantic response models in the backend are the single source of truth. The generated `api-types.ts` is committed (reviewable diffs) and regenerated in CI; a mismatch fails the build. The enums `shared/types/TODO.md` lists (ImpactType, SentimentLabel, TrafficLight, Momentum, …) live once, in Python, and flow outward. `shared/config/` constants (score bands, sector list, topic chips) become backend constants **served in the OpenAPI schema or a `GET /api/meta` payload** rather than duplicated.

## Consequences

- Jaden's hooks (`frontend/src/hooks/TODO.md`) get typed `{data, isLoading, error}` returns without anyone maintaining types by hand.
- The API contract becomes the enforced integration point between Aalind and Jaden — drift is a CI failure, not a runtime surprise.
- `development/shared/` folder is dissolved: `types/` → generated file in `frontend/src/api/`; `config/` → backend constants + `/api/meta`.
- A future second client (React Native, ADR-001) consumes the same spec.
