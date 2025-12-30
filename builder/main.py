import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .api import upload

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    logger.info("🚀 Auto-Builder Python 启动")
    logger.info(f"📦 AI Provider: {settings.ai_provider}")
    logger.info(f"🧠 Model: {settings.ai_model}")
    yield
    # 关闭时清理
    logger.info("👋 Auto-Builder Python 关闭")


app = FastAPI(
    title="Auto-Builder API",
    description="AI-powered ORM entity generator",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(upload.router, prefix="/api", tags="Upload")


@app.get("/")
async def root():
    return {"message": "Auto-Builder API is running", "version": "2.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "builder.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
