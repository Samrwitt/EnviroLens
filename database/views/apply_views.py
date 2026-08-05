"""Apply reporting views to the database."""

from pathlib import Path

from sqlalchemy import text

from database.session import engine

VIEWS = Path(__file__).with_name("reporting_views.sql")


def apply_views() -> None:
    sql = VIEWS.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Reporting views applied.")


if __name__ == "__main__":
    apply_views()
