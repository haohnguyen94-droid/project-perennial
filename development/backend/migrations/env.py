import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(BACKEND_DIR / ".env")

from src.models.base import Base  # noqa: E402  (needs sys.path set above)

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Autogenerate diffs against the models' metadata. Model classes land with
# build-order steps 2-4 (development/database/POSTGRES_SETUP.md §4); until a
# table's model exists, autogenerate simply has nothing to diff.
target_metadata = Base.metadata


def _database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set — copy development/backend/.env.example "
            "to .env (local) or set it in the service environment (Railway)."
        )
    # Railway/Heroku hand out postgres:// or postgresql:// URLs; SQLAlchemy
    # needs the psycopg driver spelled out. Accept any of the three forms.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = create_engine(_database_url(), poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
