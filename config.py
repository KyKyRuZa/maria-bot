from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Необходимо указать BOT_TOKEN в переменных окружения")

ADMIN_IDS_RAW = os.getenv("ADMIN_IDS")
if not ADMIN_IDS_RAW:
    raise ValueError("Необходимо указать ADMIN_IDS в переменных окружения")

ADMIN_IDS = [int(id_str.strip()) for id_str in ADMIN_IDS_RAW.split(",") if id_str.strip().isdigit()]
if not ADMIN_IDS:
    raise ValueError("ADMIN_IDS должен содержать хотя бы один числовой ID администратора")

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)