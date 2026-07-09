# News Intelligence Platform

AI 驱动的新闻智能平台。

## 架构

```
本地 Windows (Hermes)          云 Ubuntu (Docker)
─────────────────────         ─────────────────────
RSS Scanner                    ┌───────────────┐
    ↓                          │     Vue       │
评分 + 抓取 + AI增强             └───────▲───────┘
    ↓                                  │
POST /internal/news             ┌───────┴───────┐
    ↓                           │    FastAPI    │
    └──────────────────────────►└───────▲───────┘
                                        │
                                ┌───────┴───────┐
                                │ PostgreSQL    │
                                └───────────────┘
```

## 快速开始

### 云端部署

```bash
git clone <repo-url>
cd news-intel-platform
docker compose up -d
```

### 本地 Hermes 推送

```bash
cd search-engine-v2/scripts
export NEWS_API_BASE=http://<云主机IP>:8000
python -m news_intel.pipeline --hours 2
```

## 目录

```
news-intel-platform/
├── api/            FastAPI (Python)
│   ├── main.py
│   ├── models.py   6 tables
│   └── routes/     news / internal / categories / auth
├── web/            Vue 3 前端
│   └── src/views/  Home / Detail / Search / Category / Login
├── docker-compose.yml
└── README.md
```
