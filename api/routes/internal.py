"""routes/internal.py — Hermes → FastAPI 内部推送接口"""
import json
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import get_db
from models import Article
from schemas import ArticleIn
from sqlalchemy.dialects.postgresql import insert

router = APIRouter(prefix="/internal", tags=["internal"])

# 简单的内部认证 token（生产环境应改环境变量）
INTERNAL_TOKEN = "hermes-pipeline-secret-2026"


def verify_internal(x_internal_token: str = Header(None)):
    if x_internal_token != INTERNAL_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return True


@router.post("/news")
def push_news(article: ArticleIn, _=Depends(verify_internal), db: Session = Depends(get_db)):
    """Hermes pipeline 推送新闻。INSERT 或 UPDATE（按URL去重）。"""
    data = article.model_dump(exclude_none=True)

    # JSON 字段序列化
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
