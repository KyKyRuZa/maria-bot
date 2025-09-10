import asyncio
import logging
from config import dp, bot
import handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logging.getLogger("aiogram").setLevel(logging.WARNING)

async def main():
    logging.info("Бот mariaswimpro запускается...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())