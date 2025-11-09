from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.routers import users, recommendations, analytics
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.walrus import init_walrus

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    await init_db()
    await init_walrus()
    yield
    # 关闭时清理资源

app = FastAPI(
    title="Markov-Walrus Recommender",
    description="基于马尔科夫链和去中心化存储的推荐系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {
        "message": "Markov-Walrus 推荐系统",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )