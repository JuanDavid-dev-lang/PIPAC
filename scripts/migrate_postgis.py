from __future__ import annotations

import psycopg2
import os
from pathlib import Path

DB_URL = os.getenv("DATABASE_URL", "postgresql://crime:crime@localhost:5432/crime_ai")
HERE = Path(__file__).resolve().parents[1]
SQL_FILE = HERE / "database" / "schema.sql"


def run_migration():
    sql = SQL_FILE.read_text(encoding="utf-8")
    # psycopg2 requires dsn without +psycopg2, ensure compatibility
    dsn = DB_URL.replace("+psycopg2", "")
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.close()
    print("Migracion PostGIS aplicada.")


if __name__ == '__main__':
    run_migration()
