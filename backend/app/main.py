from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import router as api_v1_router

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="个人成长管理平台 API",
    version="0.1.0",
    debug=settings.DEBUG
)

# 配置 CORS - 允许所有来源用于本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "Welcome to High-Performance API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
