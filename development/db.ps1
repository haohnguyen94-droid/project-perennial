# Database dev workflow — Windows twin of the Makefile db-* targets.
# Usage (from development/):  .\db.ps1 up | down | upgrade | downgrade | current | psql | reset
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("up", "down", "upgrade", "downgrade", "current", "psql", "reset")]
    [string]$cmd
)

$dev = $PSScriptRoot

switch ($cmd) {
    "up"        { docker compose -f "$dev\docker-compose.yml" up -d db }
    "down"      { docker compose -f "$dev\docker-compose.yml" down }
    "upgrade"   { Push-Location "$dev\backend"; alembic upgrade head;  Pop-Location }
    "downgrade" { Push-Location "$dev\backend"; alembic downgrade -1;  Pop-Location }
    "current"   { Push-Location "$dev\backend"; alembic current;       Pop-Location }
    "psql"      { docker compose -f "$dev\docker-compose.yml" exec db psql -U perennial -d perennial }
    "reset"     {
        # LOCAL ONLY — destroys the local database volume, then re-creates.
        docker compose -f "$dev\docker-compose.yml" down -v
        docker compose -f "$dev\docker-compose.yml" up -d db
        Push-Location "$dev\backend"; alembic upgrade head; Pop-Location
    }
}
