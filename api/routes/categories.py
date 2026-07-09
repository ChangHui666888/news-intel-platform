"""routes/categories.py"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Article

router = APIRouter(tags=["categories"])


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    """所有分类及文章数"""
    rows = (
        db.query(Article.category, func.count(Article.id).label("cnt"))
        .filter(Article.is_published == True, Article.category.isnot(None))
        .group_by(Article.category)
        .order_by(func.count(Article.id).desc())
        .all()
    )
    return [{"name": r[0], "count": r[1]} for r in rows if r[0]]


@router.get("/tags")
def list_tags(db: Session = Depends(get_db)):
    """热门标签（取Top30）"""
    articles = (
        db.query(Article.tags)
        .filter(Article.is_published == True, Article.tags.isnot(None))
        .limit(500)
        .all()
    )
    from collections import Counter
    import json
    counter = Counter()
    for (tags_json,) in articles:
        try:
            tags = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
            if isinstance(tags, list):
                counter.update(tags)
        except (json.JSONDecodeError, TypeError):
            pass
    return [{"name": tag, "count": cnt} for tag, cnt in counter.most_common(30)]
