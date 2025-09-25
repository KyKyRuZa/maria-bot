from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import dp

@dp.callback_query(F.data == "open_shop")
async def open_shop(callback: CallbackQuery):
    shop_text = (
        "🛍 <b>Добро пожаловать в наш магазин!</b>\n"
        "Здесь вы найдёте всё необходимое для занятий плаванием:\n"
        "• Купальники и гидрокостюмы\n"
        "• Очки для плавания\n"
        "• Шапочки и ласты\n"
        "• Носки и перчатки для тренировок\n"
        "• Спортивные сумки и аксессуары\n\n"
        "Все товары проверены тренерами и учениками.\n"
        "Качество, комфорт и стиль — для каждого уровня подготовки!\n"
        "👉 Нажмите кнопку ниже, чтобы перейти:"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Перейти в магазин", url="https://t.me/swimthings")
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    builder.adjust(1)
    await callback.message.edit_text(shop_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()