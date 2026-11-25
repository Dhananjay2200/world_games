"""
SQLAlchemy Database Engine and Session Factory.
High-concurrency connection pooling for PostgreSQL.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings
from app.utils.logging import logger

settings = get_settings()

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DB_ECHO,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_timeout=10,     # Prevent connection pool starvation lockups under traffic spikes
        pool_recycle=1800,   # Recycle connections every 30 minutes to prevent stale TCP sockets
        pool_pre_ping=True,  # Automatically detects and discards stale/dead connections
        echo=settings.DB_ECHO,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for yielding transactional database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_models() -> None:
    """Creates all database tables and composite performance indexes if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        if "postgresql" in settings.DATABASE_URL:
            # Ensure composite indexes exist on pre-existing tables for 1M-scale filtering
            with engine.begin() as conn:
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_article_feed_status_created "
                    "ON game_articles (status, created_at DESC);"
                ))
                conn.execute(text(
                    "CREATE INDEX IF NOT EXISTS idx_article_feed_filters "
                    "ON game_articles (status, article_type, category, origin_region);"
                ))
        logger.info("[+] Database schema & high-concurrency composite indexes successfully verified/created.")
    except Exception as e:
        logger.error(f"[-] Database table initialization failed: {e}")
        raise e
