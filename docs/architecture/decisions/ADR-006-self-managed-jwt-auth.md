# ADR-006 — Self-managed JWT auth (not Auth0/Clerk)

**Status:** Accepted (architect recommendation; confirmable at next meeting) · **Deciders:** @hong (Security/Data-Privacy Lead), @aalind

## Context

`development/TODO.md` and `milestones/milestone-5/TODO.md` list "OAuth + JWT vs Auth0/Clerk" as open, assigned `@hong @aalind`. Requirements: signup/login/logout/refresh/change-password endpoints (`backend/TODO.md`), token lifetime + refresh policy + deletion implications to be documented in `AUTH_FLOW.md` (`docs/technical-specs/TODO.md`). Hong's role is Security Lead — building auth is part of the academic point.

## Options

1. **Self-managed:** argon2id hashing (`argon2-cffi`), 15-min JWT access token + 14-day rotating refresh token stored server-side (revocable).
2. Clerk/Auth0 — genuinely safer and faster; free tiers cover demo scale; but auth becomes a checkbox, hollowing out Hong's lead area and adding a third-party dependency to the demo.
3. Social OAuth (Google sign-in) on top of either — extra provider config for personas who can type an email; deferred.

## Decision

**Option 1**, with the blast radius contained by policy:

- Passwords: argon2id, library defaults; strength validation both ends (`frontend/src/utils/TODO.md` validators).
- Access token: 15 min, claims `sub`+`exp` only (no PII), held in browser memory.
- Refresh token: 14 days, rotated on every use, stored hashed in `refresh_tokens`, delivered as httpOnly SameSite cookie. Revocation on logout, on change-password (all sessions except current), on account deletion.
- No password reset via email in v1 (no email channel exists — build-plan.md §2); operator resets via CLI. *Documented limitation, acceptable for testers.*
- Rate limiting on auth endpoints (the `rate-limit` middleware in `middleware/TODO.md`).

## Consequences

- Hong ships a real auth flow and writes `AUTH_FLOW.md` from working code — strong M5 material.
- The team owns the risk of auth bugs; mitigated by using boring libraries for every cryptographic operation and an integration-test suite over the token lifecycle (`testing/integration/TODO.md` already lists the signup/login round-trip).
- **Flip condition** (mirrors [stack-decision.md](../stack-decision.md)): if the walking skeleton slips or auth work crowds out the differentiator, swap to Clerk — the seam is that auth logic lives in `AuthService` + one middleware; routes and frontend hooks (`useAuth`) keep their shape.
