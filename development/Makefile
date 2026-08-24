# Database dev workflow (Mac/Linux; Windows users: use ./db.ps1 with the same verbs)
# Docs: development/database/POSTGRES_SETUP.md §4

COMPOSE := docker compose

db-up:
	$(COMPOSE) up -d db

db-down:
	$(COMPOSE) down

db-upgrade:
	cd backend && alembic upgrade head

db-downgrade:
	cd backend && alembic downgrade -1

db-current:
	cd backend && alembic current

db-psql:
	$(COMPOSE) exec db psql -U perennial -d perennial

# LOCAL ONLY — destroys the local database volume, then re-creates.
db-reset:
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	cd backend && alembic upgrade head

.PHONY: db-up db-down db-upgrade db-downgrade db-current db-psql db-reset
