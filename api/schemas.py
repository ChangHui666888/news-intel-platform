"""schemas.py — Pydantic models"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ArticleIn(BaseModel):
    """Hermes → FastAPI internal push"""
    url: str
    title: str
    content_md: Optional[str] = None
    published_at: Optional[datetime] = None
    source_name: Optional[str] = None
    source_domain: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list] = None
    entities: Optional[dict] = None
    score_total: Optional[int] = 0
    score_breakdown: Optional[dict] = None
    tier: Optional[str] = None
    analysis: Optional[dict] = None
    summary_cn: Optional[str] = None
    summary: Optional[str] = None
    key_points: Optional[list] = None
    extraction_method: Optional[str] = None
    fetch_strategy: Optional[str] = None
    fetch_cost: Optional[int] = 0


class ArticleOut(BaseModel):
    id: int
    url: str
    title: str
    summary_cn: Optional[str] = None
    summary: Optional[str] = None
    source_name: Optional[str] = None
    source_domain: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[list] = None
    entities: Optional[dict] = None
    score_total: Optional[int] = 0
    tier: Optional[str] = None
    importance: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArticleDetail(ArticleOut):
    content_md: Optional[str] = None
    content_len: Optional[int] = 0
    analysis: Optional[dict] = None
    key_points: Optional[list] = None
    extraction_method: Optional[str] = None


class ArticleList(BaseModel):
    items: list[ArticleOut]
    total: int
    page: int
    page_size: int


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class SubscribeIn(BaseModel):
    tag: str


class SearchParams(BaseModel):
    q: str = ""
    category: Optional[str] = None
    tag: Optional[str] = None
    tier: Optional[str] = None
    page: int = 1
    page_size: int = 20
