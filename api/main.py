"""main.py — FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import news, internal, categories, auth, admin, ads

# 建表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="News Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(internal.router)
app.include_router(news.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(ads.router)


@app.get("/")
def root():
    return {"service": "News Intelligence Platform", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
