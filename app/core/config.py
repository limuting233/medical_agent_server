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

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")  # 环境变量文件路径
        case_sensitive = True  # 环境变量名称大小写敏感
        env_file_encoding = "utf-8"  # 环境变量文件编码
        extra = "ignore"  # 忽略额外的环境变量


settings = Settings()
