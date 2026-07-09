"""models.py — 6 tables"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from sqlalchemy.sql import func
from database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(2048), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    summary_cn = Column(Text)
    content_md = Column(Text)
    content_len = Column(Integer, default=0)
    source_name = Column(String(200))
    source_domain = Column(String(200))
    published_at = Column(DateTime)
    category = Column(String(100))
    importance = Column(String(20), default="medium")  # critical/high/medium/low
    tags = Column(JSON)           # ["AI","NVIDIA","芯片"]
    entities = Column(JSON)       # {"companies":[],"persons":[],"countries":[]}
    score_total = Column(Integer, default=0)
    score_breakdown = Column(JSON)
    tier = Column(String(1))      # A/B/C
    analysis = Column(JSON)       # {"event","impact","market_signal","risk_level",...}
    key_points = Column(JSON)     # ["..."]
    extraction_method = Column(String(50))
    fetch_strategy = Column(String(50))
    fetch_cost = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    level = Column(String(20), default="free")  # free/vip/admin
    expire_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    tag = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    image_url = Column(String(500))
    link_url = Column(String(500))
    position = Column(String(50), default="sidebar")  # sidebar/banner/inline
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Setting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, onupdate=func.now())


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(100))
    detail = Column(Text)
    ip = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
