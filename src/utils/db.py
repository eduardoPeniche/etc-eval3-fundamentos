import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from dotenv import load_dotenv

load_dotenv()


def get_engine() -> Engine:
    db_url = os.getenv("DB_URL", "sqlite:///./data/pollution.db")
    engine = create_engine(db_url)
    return engine


def init_db(engine: Engine = None) -> None:
    if engine is None:
        engine = get_engine()

    schema_path = Path("sql/schema.sql")
    if not schema_path.exists():
        raise FileNotFoundError("No se encontró sql/schema.sql")

    schema_sql = schema_path.read_text(encoding="utf-8")

    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))
