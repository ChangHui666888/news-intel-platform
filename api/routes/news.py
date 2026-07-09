"""routes/news.py — 新闻查询接口"""
from fastapi import APIRouter, Depends, Query, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Article, User
from schemas import ArticleOut, ArticleDetail, ArticleList
from routes.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=ArticleList)
def list_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str = Query(None),
    tag: str = Query(None),
    tier: str = Query(None),
    sort: str = Query("latest"),  # latest / hot
    db: Session = Depends(get_db),
):
    """新闻列表：分页 + 分类/标签/tier 过滤 + 排序"""
    q = db.query(Article).filter(Article.is_published == True)

    if category:
        q = q.filter(Article.category == category)
    if tag:
        q = q.filter(Article.tags.contains(tag))
    if tier:
        q = q.filter(Article.tier == tier)

    total = q.count()

    if sort == "hot":
        q = q.order_by(desc(Article.score_total))
    else:
        q = q.order_by(desc(Article.published_at))

    q = q.order_by(desc(Article.created_at))
    items = q.offset((page - 1) * page_size).limit(page_size).all()

    return ArticleList(
        items=[ArticleOut.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/hot", response_model=list[ArticleOut])
def hot_news(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    """热门新闻：按评分降序"""
    items = (
        db.query(Article)
        .filter(Article.is_published == True)
        .order_by(desc(Article.score_total), desc(Article.created_at))
        .limit(limit)
        .all()
    )
    return [ArticleOut.model_validate(a) for a in items]


@router.get("/latest", response_model=list[ArticleOut])
def latest_news(limit: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    """最新新闻"""
    items = (
        db.query(Article)
        .filter(Article.is_published == True)
        .order_by(desc(Article.published_at), desc(Article.created_at))
        .limit(limit)
        .all()
    )
    return [ArticleOut.model_validate(a) for a in items]


@router.get("/{article_id}", response_model=ArticleDetail)
def get_news(
    article_id: int,
    db: Session = Depends(get_db),
    # Optional auth — VIP gets full content, free gets summary only
    authorization: str = Header(None),
):
    """新闻详情 — VIP 用户获取全文，免费用户仅摘要"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Not found")

    result = ArticleDetail.model_validate(article)

    # 检查用户等级
    is_vip = False
    if authorization and authorization.startswith("Bearer "):
        try:
            from jose import jwt
            payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
            user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
            if user and user.level in ("vip", "admin"):
                is_vip = True
        except Exception:
            pass

    # 免费用户：隐藏正文，只保留摘要
    if not is_vip:
        result.content_md = None
        result.analysis = None
        result.key_points = None

    return result


@router.get("/search", response_model=ArticleList)
def search_news(
    q: str = Query("", min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """全文搜索（标题+摘要）"""
    from sqlalchemy import or_
    query = (
        db.query(Article)
        .filter(Article.is_published == True)
        .filter(
            or_(
                Article.title.ilike(f"%{q}%"),
                Article.summary.ilike(f"%{q}%"),
                Article.summary_cn.ilike(f"%{q}%"),
            )
        )
        .order_by(desc(Article.published_at))
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return ArticleList(
        items=[ArticleOut.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )
