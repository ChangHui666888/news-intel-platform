"""models.py — V1 Event-centric schema (11 tables + 6 associations)"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    url = Column(String(2048))
    type = Column(String(20), default="rss")
    status = Column(String(20), default="active")
    failure_count = Column(Integer, default=0)
    quarantine_until = Column(DateTime)
    last_success_at = Column(DateTime)
    credibility = Column(Float, default=0.5)
    created_at = Column(DateTime, server_default=func.now())


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    url = Column(String(2048), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    summary_cn = Column(Text)
    content_md = Column(Text)
    content_len = Column(Integer, default=0)
    published_at = Column(DateTime)
    fetched_at = Column(DateTime, server_default=func.now())
    score_total = Column(Integer, default=0)
    tier = Column(String(1))
    importance_level = Column(String(20), default="medium")
    score_breakdown = Column(JSONB)
    language = Column(String(5), default="en")
    status = Column(String(20), default="raw")
    is_duplicate = Column(Boolean, default=False)
    extraction_method = Column(String(50))
    fetch_strategy = Column(String(50))
    fetch_cost = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    source = relationship("Source")


class Entity(Base):
    __tablename__ = "entities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    type = Column(String(30), default="Organization")
    aliases = Column(JSONB, default=[])
    extra = Column("extra", JSONB, default={})
    created_at = Column(DateTime, server_default=func.now())


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(200), unique=True)
    summary = Column(Text)
    started_at = Column(DateTime)
    last_updated_at = Column(DateTime)
    article_count = Column(Integer, default=0)
    impact_level = Column(String(10), default="MEDIUM")
    category_id = Column(Integer, ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())


class Insight(Base):
    __tablename__ = "insights"
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id"), unique=True)
    generated_at = Column(DateTime, server_default=func.now())
    model = Column(String(50))
    summary = Column(Text)
    impact_analysis = Column(Text)
    drivers = Column(Text)
    sentiment = Column(String(20))
    confidence = Column(Float)
    raw_output = Column(Text)


class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(200))
    exchange = Column(String(50))


# ── Association tables ──

class ArticleEntity(Base):
    __tablename__ = "article_entity"
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True)
    relevance_score = Column(Float, default=1.0)


class EventArticle(Base):
    __tablename__ = "event_article"
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True, unique=True)


class EventEntity(Base):
    __tablename__ = "event_entity"
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
    entity_id = Column(Integer, ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True)
    importance = Column(Float, default=1.0)


class ArticleCategory(Base):
    __tablename__ = "article_category"
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)


class ArticleTag(Base):
    __tablename__ = "article_tag"
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


# ── Legacy tables (unchanged) ──

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    level = Column(String(20), default="free")
    expire_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    tag = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    image_url = Column(String(500))
    link_url = Column(String(500))
    position = Column(String(50), default="sidebar")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, onupdate=func.now())


class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    action = Column(String(100))
    detail = Column(Text)
    ip = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
