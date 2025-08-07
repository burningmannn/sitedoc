import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

LOGS_DIR = Path("logs")
os.makedirs(LOGS_DIR, exist_ok=True)


def init_logging():
    # Общий формат
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] — %(message)s', '%Y-%m-%d %H:%M:%S')

    # 🔴 Логгер ошибок и предупреждений
    error_handler = RotatingFileHandler(f"{LOGS_DIR}/errors.log", maxBytes=1000000, backupCount=3, encoding='utf-8')
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(formatter)

    # ✅ Логгер действий (например, создание пользователей)
    actions_handler = RotatingFileHandler(f"{LOGS_DIR}/actions.log", maxBytes=1000000, backupCount=3, encoding='utf-8')
    actions_handler.setLevel(logging.INFO)
    actions_handler.setFormatter(formatter)

    # 🔥 Логгер ошибок
    error_logger = logging.getLogger("errors")
    error_logger.setLevel(logging.WARNING)
    error_logger.addHandler(error_handler)
    error_logger.propagate = False

    # ✅ Логгер действий
    action_logger = logging.getLogger("actions")
    action_logger.setLevel(logging.INFO)
    action_logger.addHandler(actions_handler)
    action_logger.propagate = False

    # (опционально) если хочешь также видеть это всё в консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    error_logger.addHandler(console_handler)
    action_logger.addHandler(console_handler)


class Settings(BaseSettings):
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_HOST: str
    BASE_URL: str
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, 'app/uploads')
    STATIC_DIR: str = os.path.join(BASE_DIR, 'app/static')

    PS_DATABASE_NAME: str
    PS_DRIVER: str
    PS_USERNAME: str
    PS_PASSWORD: str
    PS_HOST: str
    PS_TABLE_NAME: str
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


settings = Settings()




