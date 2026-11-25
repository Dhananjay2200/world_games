"""
SQLAlchemy ORM Models for WorldGames AI.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database.session import Base


class GameTopic(Base):
    """Represents a discovered game/sport topic ready for research & content generation."""
    __tablename__ = "game_topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    canonical_name = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(String(100), nullable=False, index=True)
    origin_region = Column(String(100), nullable=False, index=True)
    origin_country = Column(String(150), nullable=True, index=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, PROCESSING, GENERATED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    articles = relationship("GameArticle", back_populates="topic", cascade="all, delete-orphan")


class GameArticle(Base):
    """Full-length encyclopedic guide or news story for a world game/sport."""
    __tablename__ = "game_articles"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("game_topics.id", ondelete="CASCADE"), nullable=False, index=True)
    article_type = Column(String(50), default="PLAYBOOK", index=True)  # PLAYBOOK or NEWS
    title = Column(String(300), nullable=False)
    slug = Column(String(300), unique=True, index=True, nullable=False)
    meta_description = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    
    category = Column(String(100), nullable=False, index=True)
    origin_region = Column(String(100), nullable=False, index=True)
    origin_country = Column(String(150), nullable=True, index=True)
    
    score = Column(Float, default=0.0, index=True)
    status = Column(String(50), default="PUBLISHED", index=True)  # PUBLISHED, IN_REVIEW, DRAFT
    
    primary_image_url = Column(String(1000), nullable=True)
    image_caption = Column(String(500), nullable=True)
    image_attribution = Column(String(500), nullable=True)
    image_license = Column(String(100), nullable=True)
    
    seo_keywords = Column(Text, nullable=True)
    reading_time_minutes = Column(Integer, default=6)
    
    published_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    topic = relationship("GameTopic", back_populates="articles")
    evaluations = relationship("QualityEvaluation", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_article_feed_status_created", "status", "created_at"),
        Index("idx_article_feed_filters", "status", "article_type", "category", "origin_region"),
    )


class QualityEvaluation(Base):
    """Quality Evaluation logs across the 11-dimension scoring gate."""
    __tablename__ = "quality_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("game_articles.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    passed = Column(Boolean, default=False)
    criteria_breakdown = Column(Text, nullable=True)  # JSON string
    feedback = Column(Text, nullable=True)
    revision_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("GameArticle", back_populates="evaluations")


class AutomationState(Base):
    """Tracks continuous background autonomous generation state and daily quotas."""
    __tablename__ = "automation_state"

    id = Column(Integer, primary_key=True, index=True)
    is_running = Column(Boolean, default=False)
    daily_count = Column(Integer, default=0)
    daily_limit = Column(Integer, default=200)
    last_reset_date = Column(String(50), nullable=True)  # YYYY-MM-DD
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    interval_seconds = Column(Integer, default=300)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
