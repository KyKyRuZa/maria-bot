import asyncio
import logging
import sys
from config import dp, bot
import handlers
from database.base import init_db, close_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8")
    ]
)

logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

async def main():
    logger.info("🚀 Бот запускается...")
    try:
        await init_db() 
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("💥 Критическая ошибка: %s", e)
        raise
    finally:
        await close_db()
        logger.info("🔌 Ресурсы очищены")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен вручную.")
