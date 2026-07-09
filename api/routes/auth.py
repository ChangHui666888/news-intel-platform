"""routes/auth.py — 登录/注册/鉴权（hashlib版，避免bcrypt版本冲突）"""
import os, hashlib, secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from database import get_db
from models import User, Subscription
from schemas import LoginIn, TokenOut, SubscribeIn

router = APIRouter(tags=["auth"])

SECRET_KEY = os.environ.get("JWT_SECRET", "news-intel-secret-change-me")
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    return salt + ":" + hashlib.sha256((salt + password).encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, h = hashed.split(":", 1)
        return h == hashlib.sha256((salt + password).encode()).hexdigest()
    except (ValueError, AttributeError):
        return False


def create_token(user_id: int, email: str, level: str) -> str:
    return jwt.encode(
        {"sub": str(user_id), "email": email, "level": level,
         "exp": datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm=ALGORITHM,
    )


def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(authorization[7:], SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")


def get_admin(user: User = Depends(get_current_user)) -> User:
    if user.level != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user


@router.post("/register")
def register(body: LoginIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password), level="free")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.email, user.level)
    return TokenOut(access_token=token, user={"id": user.id, "email": user.email, "level": user.level})


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id, user.email, user.level)
    return TokenOut(access_token=token, user={"id": user.id, "email": user.email, "level": user.level})


@router.get("/me")
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subs = [s.tag for s in db.query(Subscription).filter(Subscription.user_id == user.id).all()]
    return {"id": user.id, "email": user.email, "level": user.level,
            "expire_at": user.expire_at.isoformat() if user.expire_at else None,
            "subscriptions": subs}


@router.post("/subscribe")
def subscribe(body: SubscribeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.tag == body.tag).first():
        return {"status": "already_subscribed"}
    db.add(Subscription(user_id=user.id, tag=body.tag))
    db.commit()
    return {"status": "ok"}


@router.post("/unsubscribe")
def unsubscribe(body: SubscribeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Subscription).filter(Subscription.user_id == user.id, Subscription.tag == body.tag).delete()
    db.commit()
    return {"status": "ok"}


@router.post("/upgrade-vip")
def upgrade_vip(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.level = "vip"
    user.expire_at = datetime.utcnow() + timedelta(days=365)
    db.commit()
    return {"status": "ok", "level": "vip", "expire_at": user.expire_at.isoformat()}
