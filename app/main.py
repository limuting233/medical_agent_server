from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.logging import setup_logging





def create_app() -> FastAPI:
    """
    创建FastAPI应用
    :return: FastAPI应用实例
    """
    # 创建FastAPI应用实例
    app = FastAPI()

    # 配置日志
    setup_logging()

    # 配置API路由
    app.include_router(api_router, prefix="/api/v1")


    return app


app = create_app()
