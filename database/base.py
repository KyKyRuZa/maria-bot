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

for key, value in DB_CONFIG.items():
    if value is None:
        logger.warning(f"Отсутствует значение для {key} в переменных окружения")

_pool = None

async def init_db():
    global _pool
    logger.info("Начинается инициализация пула подключений к БД...")

    if _pool is None:
        try:
            logger.info(f"Подключение к БД: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
            _pool = await asyncpg.create_pool(**DB_CONFIG)
            logger.info("Пул подключений к БД успешно создан")
        except Exception as e:
            logger.critical(f"Ошибка при создании пула подключений: {str(e)}", exc_info=True)
            raise
    else:
        logger.info("🔄 Пул подключений уже существует")

create_pool = init_db

async def close_db():
    global _pool
    logger.info("🔌 Начинается закрытие пула подключений к БД...")
    if _pool:
        try:
            await _pool.close()
            _pool = None
            logger.info("Пул подключений к БД успешно закрыт")
        except Exception as e:
            logger.error(f"Ошибка при закрытии пула подключений: {str(e)}", exc_info=True)
    else:
        logger.warning("Пул подключений уже закрыт или не был инициализирован")

def get_pool():
    if _pool is None:
        logger.error("Попытка получить пул подключений до его инициализации!")
        raise RuntimeError("База данных не инициализирована! Вызовите init_db() сначала.")
    return _pool