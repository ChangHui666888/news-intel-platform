"""routes/admin.py — 后台管理"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from models import Article, User, Ad
from routes.auth import get_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def dashboard(_: User = Depends(get_admin), db: Session = Depends(get_db)):
    """后台首页统计"""
    return {
        "articles_total": db.query(func.count(Article.id)).scalar(),
        "articles_published": db.query(func.count(Article.id)).filter(Article.is_published == True).scalar(),
        "articles_by_tier": dict(db.query(Article.tier, func.count(Article.id))
                                 .filter(Article.tier.isnot(None))
                                 .group_by(Article.tier).all()),
        "users_total": db.query(func.count(User.id)).scalar(),
        "users_by_level": dict(db.query(User.level, func.count(User.id)).group_by(User.level).all()),
        "ads_active": db.query(func.count(Ad.id)).filter(Ad.is_active == True).scalar(),
    }


# ── 新闻管理 ──────────────────────────────────

@router.get("/articles")
def list_articles(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    published: bool = Query(None),
    _: User = Depends(get_admin), db: Session = Depends(get_db),
):
    q = db.query(Article)
    if published is not None:
        q = q.filter(Article.is_published == published)
    total = q.count()
    items = q.order_by(desc(Article.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [{"id": a.id, "title": a.title, "url": a.url,
                       "category": a.category, "tier": a.tier,
                       "is_published": a.is_published} for a in items],
            "total": total, "page": page}


@router.put("/articles/{article_id}/toggle")
def toggle_article(article_id: int, _: User = Depends(get_admin), db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    article.is_published = not article.is_published
    db.commit()
    return {"id": article.id, "is_published": article.is_published}


@router.delete("/articles/{article_id}")
def delete_article(article_id: int, _: User = Depends(get_admin), db: Session = Depends(get_db)):
    db.query(Article).filter(Article.id == article_id).delete()
    db.commit()
    return {"deleted": article_id}


# ── 用户管理 ──────────────────────────────────

@router.get("/users")
def list_users(page: int = Query(1), _: User = Depends(get_admin), db: Session = Depends(get_db)):
    items = db.query(User).order_by(desc(User.created_at)).offset((page-1)*20).limit(20).all()
    return {"items": [{"id": u.id, "email": u.email, "level": u.level,
                       "expire_at": u.expire_at.isoformat() if u.expire_at else None}
                      for u in items]}


@router.put("/users/{user_id}/level")
def set_level(user_id: int, level: str = "vip", _: User = Depends(get_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.level = level
        db.commit()
    return {"id": user_id, "level": level}


# ── 广告管理 ──────────────────────────────────

@router.get("/ads")
def list_ads(_: User = Depends(get_admin), db: Session = Depends(get_db)):
    return db.query(Ad).order_by(desc(Ad.created_at)).all()


@router.post("/ads")
def create_ad(ad_data: dict, _: User = Depends(get_admin), db: Session = Depends(get_db)):
    ad = Ad(**{k: v for k, v in ad_data.items() if k in ("title", "image_url", "link_url", "position")})
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return {"id": ad.id, "title": ad.title}


@router.put("/ads/{ad_id}/toggle")
def toggle_ad(ad_id: int, _: User = Depends(get_admin), db: Session = Depends(get_db)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if ad:
        ad.is_active = not ad.is_active
        db.commit()
    return {"id": ad_id, "is_active": ad.is_active}


@router.delete("/ads/{ad_id}")
def delete_ad(ad_id: int, _: User = Depends(get_admin), db: Session = Depends(get_db)):
    db.query(Ad).filter(Ad.id == ad_id).delete()
    db.commit()
    return {"deleted": ad_id}
