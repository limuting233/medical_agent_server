from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.graph.graph import init_checkpointer, close_checkpointer, init_store, close_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    :param app: FastAPI应用实例
    """
    await init_checkpointer()  # 初始化短期记忆数据库
    await init_store()  # 初始化长期记忆数据库
    yield
    await close_checkpointer()  # 关闭短期记忆数据库连接
    await close_store()  # 关闭长期记忆数据库连接


def create_app() -> FastAPI:
    """
    创建FastAPI应用
    :return: FastAPI应用实例
    """
    # 创建FastAPI应用实例
    app = FastAPI(lifespan=lifespan)

    # 配置日志
    setup_logging()

    # 配置API路由
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
