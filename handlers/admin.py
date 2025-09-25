from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import dp, ADMIN_IDS
from database.users import get_user_stats, get_all_users
from database.registrations import get_all_registrations, get_financial_report, delete_registration
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)

PAGINATION_STATE = {}

@dp.message(Command("admin"))
async def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    from keyboards.admin import get_admin_keyboard
    await message.answer("🔐 Добро пожаловать в админ-панель!", reply_markup=get_admin_keyboard())

@dp.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery):
    stats = await get_user_stats()
    text = (
        "📊 <b>Статистика пользователей</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 Всего: <b>{stats['total']}</b>\n"
        f"🏊‍♂️ Взрослых: <b>{stats['adults']}</b>\n"
        f"👶 Детей: <b>{stats['children']}</b>"
    )
    
    from keyboards.admin import get_pagination_keyboard
    reply_markup = get_pagination_keyboard(current_page=1, total_pages=1, back_callback="admin_back")
    
    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "admin_users")
async def show_all_users(callback: CallbackQuery):
    users = await get_all_users()
    if not users:
        text = "📭 Нет зарегистрированных пользователей."
        from keyboards.admin import get_pagination_keyboard
        reply_markup = get_pagination_keyboard(current_page=1, total_pages=1, back_callback="admin_back")
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
        await callback.answer()
        return

    # Устанавливаем текущую страницу для пользователя
    user_id = callback.from_user.id
    current_page = PAGINATION_STATE.get(user_id, 1)
    per_page = 5
    total_pages = (len(users) + per_page - 1) // per_page  # ceil division

    # Ограничиваем страницу в допустимых пределах
    current_page = max(1, min(current_page, total_pages))
    PAGINATION_STATE[user_id] = current_page

    # Получаем данные для текущей страницы
    start_idx = (current_page - 1) * per_page
    end_idx = start_idx + per_page
    page_users = users[start_idx:end_idx]

    # Формируем текст
    text = f"📋 <b>Все пользователи (Страница {current_page}/{total_pages})</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for u in page_users:
        phone = u['phone'] or "не указан"
        text += (
            f"👤 <b>{u['full_name']}</b>\n"
            f"🔢 ID: <code>{u['user_id']}</code>\n"
            f"🎂 Возраст: {u['age']}\n"
            f"👥 Роль: {u['role']}\n"
            f"📱 Телефон: {phone}\n"
            f"📅 {u['registered_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        )

    from keyboards.admin import get_pagination_keyboard
    reply_markup = get_pagination_keyboard(
        current_page=current_page, 
        total_pages=total_pages, 
        back_callback="admin_back",
        page_prefix="admin_users_page_"
    )

    await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    await callback.answer()
    
@dp.callback_query(F.data.startswith("admin_users_page_"))
async def handle_page_change(callback: CallbackQuery):
    page_num = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    PAGINATION_STATE[user_id] = page_num
    await show_all_users(callback)

@dp.callback_query(F.data == "admin_registrations")
async def show_registrations(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ У вас нет доступа.")
        return

    registrations = await get_all_registrations()
    if not registrations:
        text = "📭 Нет записавшихся пользователей."
        from keyboards.admin import get_pagination_keyboard
        reply_markup = get_pagination_keyboard(current_page=1, total_pages=1, back_callback="admin_back")
        await callback.message.edit_text(text, reply_markup=reply_markup)
        await callback.answer()
        return

    # Устанавливаем текущую страницу для пользователя
    user_id = callback.from_user.id
    current_page = PAGINATION_STATE.get(f"reg_{user_id}", 1)  # Уникальный ключ для регистраций
    per_page = 5  # Ограничение в 5 пользователей на страницу
    total_pages = (len(registrations) + per_page - 1) // per_page  # ceil division

    # Ограничиваем страницу в допустимых пределах
    current_page = max(1, min(current_page, total_pages))
    PAGINATION_STATE[f"reg_{user_id}"] = current_page

    # Получаем данные для текущей страницы
    start_idx = (current_page - 1) * per_page
    end_idx = start_idx + per_page
    page_registrations = registrations[start_idx:end_idx]

    # Формируем текст с информацией о странице
    text = f"👥 <b>Кто записался на тренировки (Страница {current_page}/{total_pages})</b>\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    builder = InlineKeyboardBuilder()

    for i, r in enumerate(page_registrations, start=start_idx + 1):
        phone = r['phone'] or "не указан"
        word = "тренировка" if r['session_count'] == 1 else "тренировки" if r['session_count'] in (2,3,4) else "тренировок"
        price_text = f"{r['price']:,} ₽".replace(",", " ")

        text += (
            f"<b>{i}.</b> 👤 <b>{r['full_name']}</b>\n"
            f"   🔢 ID: <code>{r['user_id']}</code>\n"
            f"   🎯 {r['role']}, {r['age']} лет\n"
            f"   📞 {phone}\n"
            f"   ⏰ {r['training_time']}\n"
            f"   🎟 {r['session_count']} {word}\n"
            f"   💰 {price_text}\n"
            f"   📅 {r['registered_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        )
        builder.button(
            text=f"🗑 Удалить #{i}",
            callback_data=f"delete_reg_{r['user_id']}"
        )

    # Используем универсальную панель навигации
    from keyboards.admin import get_pagination_keyboard
    pagination_markup = get_pagination_keyboard(
        current_page=current_page, 
        total_pages=total_pages, 
        back_callback="admin_back",
        page_prefix="admin_registrations_page_"  # Новый префикс для пагинации регистраций
    )
    
    builder.adjust(1)
    
    final_builder = InlineKeyboardBuilder()
    
    # Добавляем кнопки удаления
    for button in builder.buttons:
        final_builder.add(button)
    final_builder.adjust(1)
    
    # Добавляем кнопки пагинации
    for row in pagination_markup.inline_keyboard:
        for button in row:
            final_builder.add(button)
        final_builder.adjust(1)  # Каждая строка отдельно

    await callback.message.edit_text(text, reply_markup=final_builder.as_markup(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("admin_registrations_page_"))
async def handle_registrations_page_change(callback: CallbackQuery):
    page_num = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id
    PAGINATION_STATE[f"reg_{user_id}"] = page_num
    await show_registrations(callback)

@dp.callback_query(F.data.startswith("delete_reg_"))
async def delete_registration_handler(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        logger.warning(f"🚫 Попытка доступа к удалению записи без прав: user_id={callback.from_user.id}")
        await callback.answer("❌ У вас нет доступа.")
        return

    try:
        user_id = int(callback.data.split("_", 2)[2])
    except (ValueError, IndexError):
        logger.error(f"❌ Неверный формат callback_data для удаления: {callback.data}")
        await callback.answer("❌ Неверный ID.")
        return

    success = await delete_registration(user_id)
    if success:
        await callback.answer(f"✅ Запись пользователя {user_id} удалена.")
    else:
        await callback.answer(f"⚠️ Запись для пользователя {user_id} не найдена.")

    await show_registrations(callback)

@dp.callback_query(F.data == "admin_back")
async def back_to_admin(callback: CallbackQuery):
    from keyboards.admin import get_admin_keyboard
    await callback.message.edit_text("🔐 Админ-панель:", reply_markup=get_admin_keyboard())
    await callback.answer()