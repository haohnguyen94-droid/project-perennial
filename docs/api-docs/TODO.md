# `docs/api-docs/` — TODO

Documentation for every API endpoint.

**Owner:** `@aalind`

---

## Format

Pick one and stick with it:
- [ ] **OpenAPI / Swagger** — recommended (auto-generates client + UI)
- [ ] Markdown per endpoint
- [ ] Postman collection

---

## What to document per endpoint

- HTTP method + path
- Auth required? (yes/no, what scope)
- Path params, query params, request body schema
- Response shape with example
- Possible error codes
- Rate limit applied

---

## Endpoints to document

Same list as in `../../development/backend/TODO.md` — keep them in sync.

---

## Conventions

- Update API docs **in the same PR** as the endpoint code
- Mark deprecated endpoints for one milestone before removing
- Include realistic example payloads
