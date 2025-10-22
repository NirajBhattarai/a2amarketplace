import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Create a PostgreSQL connection using env var CARBON_MARKETPLACE_DATABASE_URL.
    Falls back to the agent's default DSN if not set.
    """
    dsn = os.getenv(
        "CARBON_MARKETPLACE_DATABASE_URL",
        "postgresql://postgres:password@localhost:5432/carbon_credit_iot",
    )
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    return conn


def run_sql_file(conn, sql_path: str) -> None:
    with open(sql_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)


def fetch_all(query: str, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or [])
            return cur.fetchall()
    finally:
        conn.close()


def execute(query: str, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or [])
    finally:
        conn.close()


