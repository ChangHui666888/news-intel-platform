"""routes/auth.py"""
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext
from database import get_db
from models import User, Subscription
from schemas import LoginIn, TokenOut, SubscribeIn

router = APIRouter(tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET", "news-intel-secret-key-change-me")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: int, email: str, level: str) -> str:
    return jwt.encode(
        {"sub": str(user_id), "email": email, "level": level,
         "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm=ALGORITHM,
    )


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    """简易 JWT 验证 — 从 Header 读取"""
    from fastapi import Header
    auth_header = None
    # 这里简化：通过依赖注入
    return None  # 实际使用时需完善


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id, user.email, user.level)
    return TokenOut(
        access_token=token,
        user={"id": user.id, "email": user.email, "level": user.level},
    )


@router.post("/subscribe")
def subscribe(body: SubscribeIn, db: Session = Depends(get_db)):
    """标签订阅（简化版，生产需验证用户）"""
    sub = Subscription(user_id=1, tag=body.tag)  # user_id=1 为默认demo用户
    db.add(sub)
    db.commit()
    return {"status": "ok"}
