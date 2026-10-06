"""Tiny schema upgrader.

`Base.metadata.create_all` creates missing tables but never adds columns to a table
that already exists, so someone with an older shopfin.db would hit "no such column".
This adds any new columns once, and works on SQLite, PostgreSQL and MySQL.
"""
from sqlalchemy import inspect, text

from app.database.database import engine

NEW_COLUMNS: dict[str, list[tuple[str, str]]] = {
    "businesses": [("opening_cash", "NUMERIC(12, 2) NOT NULL DEFAULT 0")],
}


def ensure_columns() -> None:
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, columns in NEW_COLUMNS.items():
            if not insp.has_table(table):
                continue
            existing = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in columns:
                if name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))
