"""routes/internal.py — Hermes → FastAPI 内部推送接口"""
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Article
from schemas import ArticleIn
from sqlalchemy.dialects.postgresql import insert

router = APIRouter(prefix="/internal", tags=["internal"])
INTERNAL_TOKEN = "hermes-pipeline-secret-2026"


def verify_internal(x_internal_token: str = Header(None)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


@router.post("/news")
def push_news(article: ArticleIn, _=Depends(verify_internal), db: Session = Depends(get_db)):
    """单篇推送（保留兼容）"""
    data = article.model_dump(exclude_none=True)
    for field in ["tags", "entities", "key_points", "analysis", "score_breakdown"]:
        if data.get(field) is not None and not isinstance(data[field], str):
            data[field] = json.dumps(data[field], ensure_ascii=False)
    stmt = insert(Article).values(**data)
    stmt = stmt.on_conflict_do_update(
        index_elements=["url"],
        set_={k: stmt.excluded[k] for k in data if k != "url"}
    )
    db.execute(stmt)
    db.commit()
    return {"status": "ok", "url": article.url}


@router.post("/news/batch")
def push_news_batch(articles: List[ArticleIn], _=Depends(verify_internal), db: Session = Depends(get_db)):
    """批量推送 — 一次请求写入多篇"""
    ok = fail = 0
    for article in articles:
        try:
            data = article.model_dump(exclude_none=True)
            for field in ["tags", "entities", "key_points", "analysis", "score_breakdown"]:
                if data.get(field) is not None and not isinstance(data[field], str):
                    data[field] = json.dumps(data[field], ensure_ascii=False)
            stmt = insert(Article).values(**data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["url"],
                set_={k: stmt.excluded[k] for k in data if k != "url"}
            )
            db.execute(stmt)
            ok += 1
        except Exception:
            fail += 1
    db.commit()
    return {"ok": ok, "fail": fail}
