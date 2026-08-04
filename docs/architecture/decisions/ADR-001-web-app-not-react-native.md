# ADR-001 — Web app (React), not React Native

**Status:** Accepted (team answer, 2026-08-03) · **Deciders:** whole team (was an open item in `development/TODO.md`)

## Context

`development/TODO.md` and `milestones/milestone-5/TODO.md` list "React Native (mobile) vs React (web)" as a blocking decision. The design artifacts pull both ways: Figma exports are specified at 375 px mobile-first (`design/wireframes/figma-exports/TODO.md`), while the UI kit specs a "left sidebar nav — used on desktop/wide views" (`design/ui-kit/TODO.md`). The audience is graders and 5–8 user testers (demo scale).

## Options

1. **React web app, mobile-first responsive** — one URL, no install.
2. **React Native (Expo)** — native feel; app-store/TestFlight distribution friction; a second build/test toolchain.
3. Both via Expo Web — compromise rendering quality on the web side, tooling overhead of RN anyway.

## Decision

**Option 1.** Mobile-first responsive React SPA (Vite + TypeScript). Layouts honor the 375-px wireframes first; the sidebar appears at wide breakpoints, bottom-tab-style nav on narrow ones (resolves the `ui-kit/TODO.md` open question "left sidebar vs bottom tab bar" as: both, by breakpoint).

## Consequences

- Graders and testers click a link — zero install friction for exactly the population that matters (Q4).
- One toolchain for Jaden; routing = React Router (the `frontend/TODO.md` web branch).
- No push notifications from the home screen — irrelevant, since notification delivery is deferred anyway (build-plan.md §2).
- A future RN client remains possible: the API is client-agnostic and the OpenAPI-generated types (ADR-010) would serve it too.
