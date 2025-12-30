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
    description="AI 驱动的 ORM 实体生成器，上传 JSON 配置文件自动生成 MyBatis 代码",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
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
app.include_router(upload.router, tags=["任务管理"])


@app.get("/", summary="服务信息", tags=["系统"])
async def root():
    """获取 API 服务信息"""
    return {"message": "Auto-Builder API is running", "version": "2.0.0"}


@app.get("/health", summary="健康检查", tags=["系统"])
async def health():
    """检查服务健康状态"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "builder.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
