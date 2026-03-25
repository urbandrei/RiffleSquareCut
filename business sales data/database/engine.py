from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).resolve().parent.parent / "sales.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


class Base(DeclarativeBase):
    pass


SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _migrate_db():
    """Add columns that may be missing from older schemas."""
    import sqlite3
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(invoices)")
    columns = {row[1] for row in cursor.fetchall()}
    if "email_sent_at" not in columns:
        cursor.execute("ALTER TABLE invoices ADD COLUMN email_sent_at DATETIME")
        conn.commit()
    if "payable_to" not in columns:
        cursor.execute("ALTER TABLE invoices ADD COLUMN payable_to VARCHAR(200)")
        conn.commit()
    if "project_name" not in columns:
        cursor.execute("ALTER TABLE invoices ADD COLUMN project_name VARCHAR(200)")
        conn.commit()
    if "adjustments" not in columns:
        cursor.execute("ALTER TABLE invoices ADD COLUMN adjustments NUMERIC(10,2) DEFAULT 0")
        conn.commit()

    cursor.execute("PRAGMA table_info(customers)")
    columns = {row[1] for row in cursor.fetchall()}
    if "current_stock" not in columns:
        cursor.execute("ALTER TABLE customers ADD COLUMN current_stock INTEGER DEFAULT 0")
        conn.commit()

    conn.close()


def init_db():
    """Create all tables."""
    from . import models  # noqa: F401 — ensure models are registered
    Base.metadata.create_all(bind=engine)
    _migrate_db()
