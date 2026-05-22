from collections.abc import Generator

from sqlalchemy import create_engine, inspect
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    return database_url


database_url = normalize_database_url(settings.database_url)
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_existing_schema()


def _ensure_existing_schema() -> None:
    statements = []
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if engine.dialect.name == "postgresql":
        statements.extend(
            [
                "ALTER TABLE page_results ALTER COLUMN verdict TYPE TEXT",
                "ALTER TABLE page_results ALTER COLUMN scoring_context TYPE TEXT",
            ]
        )

    if "issues" in table_names and "line_id" not in {column["name"] for column in inspector.get_columns("issues")}:
        statements.append("ALTER TABLE issues ADD COLUMN line_id VARCHAR(16)")
    if "rewrites" in table_names and "line_id" not in {column["name"] for column in inspector.get_columns("rewrites")}:
        statements.append("ALTER TABLE rewrites ADD COLUMN line_id VARCHAR(16)")
    if "scans" in table_names:
        scan_columns = {column["name"] for column in inspector.get_columns("scans")}
        if "user_id" not in scan_columns:
            statements.append("ALTER TABLE scans ADD COLUMN user_id VARCHAR(36)")
        if "site_id" not in scan_columns:
            statements.append("ALTER TABLE scans ADD COLUMN site_id INTEGER")
        if "scan_mode" not in scan_columns:
            statements.append("ALTER TABLE scans ADD COLUMN scan_mode VARCHAR(32) DEFAULT 'free'")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
