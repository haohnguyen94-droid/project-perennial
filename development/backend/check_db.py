"""Sanity-check the database DATABASE_URL points at: version, tables, extensions.

Usage: set DATABASE_URL (or rely on .env), then `python check_db.py`.
Read-only — safe against production.
"""

import os

from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine, text

load_dotenv(Path(__file__).resolve().parent / ".env")

url = os.environ["DATABASE_URL"]
if url.startswith("postgres://"):
    url = "postgresql+psycopg://" + url[len("postgres://"):]
elif url.startswith("postgresql://"):
    url = "postgresql+psycopg://" + url[len("postgresql://"):]

engine = create_engine(url)
with engine.connect() as conn:
    print("server:", conn.execute(text("SHOW server_version")).scalar())
    tables = sorted(
        r[0] for r in conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
    )
    print("tables:", ", ".join(tables))
    exts = sorted(
        r[0] for r in conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname IN ('citext','pg_trgm')"))
    )
    print("extensions:", ", ".join(exts))
    rev = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
    print("alembic revision:", rev)
