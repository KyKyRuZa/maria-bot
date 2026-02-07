import asyncio
import logging
import sys
from config import dp, bot
import handlers
from database.base import init_db, close_db
from logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

async def main():
    logger.info("Запуск бота начинается...")
    
    logger.info(f"Python версия: {sys.version}")
    
    try:
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных инициализирована успешно")
        
        logger.info("Начало опроса сообщений...")
        await dp.start_polling(bot)
        logger.info(" polling завершен")
        
    except Exception as e:
        logger.critical("Критическая ошибка при запуске бота: %s", str(e), exc_info=True)
        raise
    finally:
        logger.info("Закрытие соединений с базой данных...")
        await close_db()
        logger.info("Ресурсы очищены, бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот принудительно остановлен пользователем")
    except Exception as e:
        logger.critical("💥 Необработанная ошибка в главном потоке: %s", str(e), exc_info=True)
