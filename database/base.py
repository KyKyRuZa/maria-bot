import asyncpg
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

_pool = None

async def init_db():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(**DB_CONFIG)
        logger.info("🔌 Пул подключений к БД успешно создан")

create_pool = init_db

async def close_db():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("🔌 Пул подключений к БД закрыт")

def get_pool():
    if _pool is None:
        raise RuntimeError("База данных не инициализирована! Вызовите init_db() сначала.")
    return _pool