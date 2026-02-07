from config import bot, ADMIN_IDS
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from utils.sanitization import sanitize_html

logger = logging.getLogger(__name__)

async def notify_admins_new_registration(registration_data: dict):
    try:
        sanitized_full_name = sanitize_html(registration_data['full_name'])
        sanitized_training_time = sanitize_html(registration_data['training_time'])

        text = (
            "🔥 <b>НОВАЯ ЗАПИСЬ!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 {sanitized_full_name}\n"
            f"⏰ {sanitized_training_time}\n"
        ).replace(",", " ")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Все записи", callback_data="admin_registrations")]
        ])

        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, text, reply_markup=keyboard, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Ошибка отправки админу {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка уведомления: {e}")