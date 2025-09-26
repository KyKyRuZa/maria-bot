from aiogram import F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from config import dp
from data.text_content import TRAINING_TIME_RU, TRAINING_SLOTS, SERVICE_TYPE_RU
from database.users import get_user_role
from database.prices import load_prices
from database.registrations import save_registration
from database.base import get_pool
from notifications import notify_admins_new_registration
from keyboards.training_selection import get_adult_pool_keyboard, get_child_pool_keyboard, get_adult_schedule_keyboard, get_child_schedule_keyboard

@dp.callback_query(F.data == "register_training")
async def choose_training(callback: CallbackQuery, state: FSMContext):
    role = await get_user_role(callback.from_user.id)
    if not role:
        await callback.message.edit_text("❌ Вы не зарегистрированы.")
        await callback.answer()
        return
    if role == "Взрослый":
        text = "🏊‍♂️ <b>Выберите бассейн для взрослых</b>"
        keyboard = get_adult_pool_keyboard()
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        text = "🧒 <b>Выберите бассейн для детей</b>"
        keyboard = get_child_pool_keyboard()
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state("choosing_pool")
    await callback.answer()

@dp.callback_query(F.data.startswith("adult_pool_"))
async def choose_adult_pool(callback: CallbackQuery, state: FSMContext):
    pool_key = callback.data.replace("adult_pool_", "")
    await state.update_data(selected_pool=pool_key)
    keyboard = get_adult_schedule_keyboard(pool_key)
    pool_name = "Адмиралтейский" if pool_key == "admiralteysky" else "ДВВС"
    text = f"🏊‍♂️ <b>Выберите время тренировки</b>\n📍 Бассейн: {pool_name}"
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state("choosing_time")
    await callback.answer()

@dp.callback_query(F.data.startswith("pool_"))
async def choose_child_pool(callback: CallbackQuery, state: FSMContext):
    pool_key = callback.data.split("_", 1)[1]
    await state.update_data(selected_pool=pool_key)
    keyboard = get_child_schedule_keyboard(pool_key)
    text = f"🧒 <b>Выберите время тренировки</b>\n📍 Бассейн: {pool_key.upper()}"
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state("choosing_time")
    await callback.answer()

@dp.callback_query(F.data.in_(TRAINING_SLOTS))
async def show_price_options(callback: CallbackQuery, state: FSMContext):
    slot = callback.data
    time_text = TRAINING_TIME_RU.get(slot, "неизвестное время")
    role = await get_user_role(callback.from_user.id)
    category = "adult" if role == "Взрослый" else "child"
    prices = await load_prices()
    prices = [p for p in prices if p['category'] == category]
    if not prices:
        await callback.message.edit_text("❌ Не удалось загрузить прайс.")
        return

    grouped = {}
    for p in prices:
        service_type = p['service_type']
        duration = p['duration'] or '45 мин'
        key = f"{service_type}_{duration}"
        if key not in grouped:
            grouped[key] = {}
        grouped[key][p['session_count']] = p

    builder = InlineKeyboardBuilder()
    for key, items_dict in grouped.items():
        first_item = next(iter(items_dict.values()))
        service_ru = SERVICE_TYPE_RU.get(first_item['service_type'], first_item['service_type'])
        duration = first_item['duration'] or '45 мин'
        builder.row(InlineKeyboardButton(text=f"📌 {service_ru} ({duration})", callback_data="header"))
        for session_count in sorted(items_dict.keys()):
            p = items_dict[session_count]
            word = "тренировка" if p['session_count'] == 1 else "тренировки" if p['session_count'] in (2,3,4) else "тренировок"
            builder.button(text=f"🎟 {p['session_count']} {word} — {p['price']} ₽", callback_data=f"price_{p['id']}")
        builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="register_training"))
    await state.update_data(selected_time_slot=slot, selected_time_text=time_text)
    await callback.message.edit_text(
        f"🏊‍♂️ <b>Выберите абонемент</b>\n"
        f"⏰ <b>Время:</b> {time_text}\n"
        f"🎯 <b>Роль:</b> {role}\n"
        "Выберите количество тренировок:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("price_"))
async def finalize_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'selected_time_slot' not in data or 'selected_time_text' not in data:
        builder = InlineKeyboardBuilder()
        builder.button(text="🏠 В главное меню", callback_data="back_to_main")
        await callback.message.edit_text(
            "❌ Произошла ошибка: данные о времени утеряны.\nПожалуйста, начните запись заново.",
            reply_markup=builder.as_markup()
        )
        await state.clear()
        await callback.answer()
        return

    price_id = int(callback.data.split("_", 1)[1])
    slot = data['selected_time_slot']
    time_text = data['selected_time_text']
    user_id = callback.from_user.id
    role = data.get('role') or await get_user_role(user_id)
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id = $1", user_id)
        price_row = await conn.fetchrow("SELECT * FROM prices WHERE id = $1", price_id)

    if not row or not price_row:
        await callback.message.edit_text("❌ Ошибка загрузки данных.")
        await state.clear()
        await callback.answer()
        return

    full_name = row['full_name']
    session_count = price_row['session_count']
    price = price_row['price']

    await save_registration(user_id, full_name, role, time_text, session_count, price )

    registration_data = {
        'full_name': full_name,
        'training_time': time_text,
    }
    await notify_admins_new_registration(registration_data)

    word = "тренировка" if session_count == 1 else "тренировки" if session_count in (2,3,4) else "тренировок"
    price_text = f"{price:,} ₽".replace(",", " ")
    success_text = (
        "✅ <b>Вы успешно записаны!</b>\n"
        f"👤 <b>ФИО:</b> {full_name}\n"
        f"🎯 <b>Роль:</b> {role}\n"
        f"⏰ <b>Время:</b> {time_text}\n"
        f"🎟 <b>Абонемент:</b> {session_count} {word}\n"
        f"💰 <b>Цена:</b> {price_text}\n"
        "📞 При необходимости изменения — свяжитесь с администратором: +7 917 899 5088"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    await callback.message.edit_text(success_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
    await state.clear()

@dp.callback_query(F.data == "show_my_registrations")
async def show_my_registrations(callback: CallbackQuery):
    from database.registrations import get_user_registration
    from database.users import get_user_role
    from keyboards.main_menu import get_main_keyboard

    user_id = callback.from_user.id
    current_role = await get_user_role(user_id)
    if not current_role:
        await callback.message.edit_text("❌ Вы не зарегистрированы.", reply_markup=get_main_keyboard(is_registered=False))
        await callback.answer()
        return

    registration = await get_user_registration(user_id)
    if not registration:
        text = "📭 <b>Вы пока никуда не записаны.</b>\nНажмите «Записаться», чтобы выбрать время и занятие."
    else:
        time_text = registration['training_time']
        session_count = registration['session_count']
        price = registration['price']
        full_name = registration['full_name']
        word = "тренировка" if session_count == 1 else "тренировки" if session_count in (2,3,4) else "тренировок"
        price_text = f"{price:,} ₽".replace(",", " ")
        text = (
            "📋 <b>Ваши записи</b>\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>ФИО:</b> {full_name}\n"
            f"🎯 <b>Роль:</b> {current_role}\n"
            f"⏰ <b>Время:</b> {time_text}\n"
            f"🎟 <b>Абонемент:</b> {session_count} {word}\n"
            f"💰 <b>Цена:</b> {price_text}\n"
            "Спасибо, что занимаетесь с нами! 🏊‍♂️"
        )
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()