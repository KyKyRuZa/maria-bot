from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from config import dp
from data.text_content import ADULT_SCHEDULE, CHILD_SCHEDULE, MEDICAL_REQUIREMENTS, CONTACTS_TEXT, COACHES_TEXT
from database.users import get_user_role
from data.price_formatter import format_pricelist_for_adults, format_pricelist_for_children
from aiogram.fsm.context import FSMContext

def _get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    return builder.as_markup()

@dp.callback_query(F.data == "show_schedule")
async def show_schedule(callback: CallbackQuery, state: FSMContext) -> None:
    role = await get_user_role(callback.from_user.id)
    if not role:
        await callback.message.edit_text("⚠️ Вы не зарегистрированы.")
        await callback.answer()
        return
    text = ADULT_SCHEDULE if role == "Взрослый" else CHILD_SCHEDULE
    await callback.message.edit_text(text, reply_markup=_get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "show_pricelist")
async def show_pricelist(callback: CallbackQuery):
    user_id = callback.from_user.id
    role = await get_user_role(user_id)
    if not role:
        text = "⚠️ Сначала пройдите регистрацию."
    else:
        if role == "Взрослый":
            text = await format_pricelist_for_adults()
        else:
            text = await format_pricelist_for_children()
    await callback.message.edit_text(text, reply_markup=_get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "show_requirements")
async def show_requirements(callback: CallbackQuery):
    await callback.message.edit_text(MEDICAL_REQUIREMENTS, reply_markup=_get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "show_contacts")
async def show_addresses(callback: CallbackQuery):
    await callback.message.edit_text(CONTACTS_TEXT, reply_markup=_get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "show_coaches")
async def show_coaches(callback: CallbackQuery):
    await callback.message.edit_text(COACHES_TEXT, reply_markup=_get_back_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "show_certificates")
async def show_certificates(callback: CallbackQuery):
    text = (
        "🎁 <b>Подарочный сертификат</b>\n"
        "Хотите подарить близкому человеку здоровье и радость плавания?\n"
        "📞 <b>Позвоните по номеру и закажите сертификат!</b>\n"
        "<code>+7(917)855-53-88</code>\n"
        "Скидка 10%\n"
        "Подарок"
    )
    await callback.message.edit_text(text, reply_markup=_get_back_keyboard(), parse_mode="HTML")
    await callback.answer()