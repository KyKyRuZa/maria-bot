from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from config import dp
from database.users import get_user_role
from database.base import get_pool

@dp.callback_query(F.data == "show_profile")
async def show_profile(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    role = await get_user_role(user_id)
    if not role:
        from keyboards.main_menu import get_main_keyboard
        await callback.message.edit_text("❌ Вы не зарегистрированы.", reply_markup=get_main_keyboard(is_registered=False))
        await callback.answer()
        return

    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name, age, phone FROM users WHERE user_id = $1", user_id)

    if not row:
        await callback.message.edit_text("❌ Не удалось загрузить данные профиля.")
        await callback.answer()
        return

    phone = row['phone'] or "не указан"
    profile_text = (
        "👤 <b>Мой профиль</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>ФИО:</b> {row['full_name']}\n"
        f"🎂 <b>Возраст:</b> {row['age']}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"🎯 <b>Роль:</b> {role}\n"
        "Вы зарегистрированы в школе плавания <b>mariaswimpro</b>!"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    await callback.message.edit_text(profile_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()