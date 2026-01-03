import os.path
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 项目根目录


class Settings(BaseSettings):
    """
    应用配置类
    """
    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    # OpenAI API配置
    OPENAI_API_BASE: str  # OPENAI API 基础URL
    OPENAI_API_KEY: str  # OpenAI API密钥

    # 数据库配置
    DB_HOST: str  # 数据库主机地址
    DB_PORT: int  # 数据库端口号
    DB_NAME: str  # 数据库名称
    DB_USER: str  # 数据库用户名
    DB_PASSWORD: str  # 数据库密码

    @property
    def DB_URL(self) -> str:
        """
        PostgreSQL 数据库连接URL
        """
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode=disable"

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")  # 环境变量文件路径
        case_sensitive = True  # 环境变量名称大小写敏感
        env_file_encoding = "utf-8"  # 环境变量文件编码
        extra = "ignore"  # 忽略额外的环境变量


settings = Settings()
