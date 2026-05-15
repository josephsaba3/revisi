from app.database import normalize_database_url


def test_normalize_database_url_accepts_common_postgres_urls() -> None:
    assert (
        normalize_database_url("postgresql://user:pass@example.com:5432/db")
        == "postgresql+psycopg://user:pass@example.com:5432/db"
    )
    assert (
        normalize_database_url("postgres://user:pass@example.com:5432/db")
        == "postgresql+psycopg://user:pass@example.com:5432/db"
    )


def test_normalize_database_url_leaves_explicit_driver_and_sqlite_alone() -> None:
    assert normalize_database_url("postgresql+psycopg://user:pass@example.com/db") == "postgresql+psycopg://user:pass@example.com/db"
    assert normalize_database_url("sqlite:///./local.db") == "sqlite:///./local.db"
