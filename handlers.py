# handlers.py
import logging
from typing import Dict, Any
import os
from dotenv import load_dotenv
from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

load_dotenv()

# --- Импорты из проекта ---
from config import dp

from data import (
    WELCOME_MESSAGE,
    MEDICAL_REQUIREMENTS,
    ADULT_SCHEDULE,
    CHILD_SCHEDULE,
    format_pricelist_for_adults,
    format_pricelist_for_children,
    CONTACTS_TEXT,
    COACHES_TEXT
)

from keyboards import (
    get_main_keyboard,
    get_role_keyboard,
    get_adult_schedule_keyboard,
    get_child_pool_keyboard,
    get_child_schedule_keyboard,
    get_admin_keyboard,
    get_edit_price_category_keyboard,
    get_adult_pool_keyboard
)

from database import (
    get_all_registrations,
    get_user_registration,
    save_user,
    get_user_role,
    get_user_stats,
    get_all_users,
    get_financial_report,
    load_prices,
    update_price,
    create_pool,
    save_registration
)

logger = logging.getLogger(__name__)

# 🔐 Укажите ваш Telegram ID
ADMIN_ID = int(os.getenv("ADMIN_ID")) # 🔥 Замените на ваш ID!

# --- Словари перевода ---
SERVICE_TYPE_RU: Dict[str, str] = {
    "group": "Групповые",
    "personal": "Персональные",
    "split": "Сплит-тренировки",
    "mini_group": "Мини-группы"
}

CATEGORY_RU: Dict[str, str] = {
    "adult": "Взрослые",
    "child": "Дети"
}

# --- Время тренировок и слоты ---
TRAINING_TIME_RU: Dict[str, str] = {
    # Взрослые
    "adult_admiralteysky_mf_2000": "Понедельник и Пятница, 20:00 (Адмиралтейский)",
    "adult_dvvs_wed_2015": "Среда, 20:15 (ДВВС)",
    # Дети - А-Фитнес
    "child_a_fitnes_tt_1545": "Вторник и Четверг, 15:45 (А-Фитнес)",
    "child_a_fitnes_sa_1415": "Суббота, 14:15 (А-Фитнес)",
    "child_a_fitnes_sa_1500": "Суббота, 15:00 (А-Фитнес)",
    "child_a_fitnes_mf_1500": "Понедельник и Пятница, 15:00 (А-Фитнес)",
    "child_a_fitnes_mf_1545": "Понедельник и Пятница, 15:45 (А-Фитнес)",
    "child_a_fitnes_wed_1500": "Среда, 15:00 (А-Фитнес)",
    "child_a_fitnes_wed_1545": "Среда, 15:45 (А-Фитнес)",
    "child_a_fitnes_mf_0945": "Вторник и Пятница, 9:45 (А-Фитнес)",
    # Мини-группы А-Фитнес
    "child_mini_a_fitnes_tt_1630": "Вторник и Четверг, 16:30 (А-Фитнес)",
    "child_mini_a_fitnes_tt_2015": "Вторник и Четверг, 20:15 (А-Фитнес)",
    "child_mini_a_fitnes_mf_2015": "Понедельник и Пятница, 20:15 (А-Фитнес)",
    "child_mini_a_fitnes_wed_2015": "Среда, 20:15 (А-Фитнес)",
    # Дети - ДВВС
    "child_dvvs_wed_1845": "Среда, 18:45 (ДВВС)",
    "child_dvvs_wed_1930": "Среда, 19:30 (ДВВС)",
    "child_dvvs_wed_2015": "Среда, 20:15 (ДВВС)",
}

TRAINING_SLOTS = set(TRAINING_TIME_RU.keys())

# --- Состояния ---
class RegistrationStates:
    waiting_for_full_name: str = "waiting_for_full_name"
    waiting_for_age: str = "waiting_for_age"
    waiting_for_role: str = "waiting_for_role"
    waiting_for_phone: str = "waiting_for_phone"

class PriceEditStates:
    waiting_for_price: str = "waiting_for_price"

# --- Основные обработчики ---

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    user = message.from_user
    logger.info(f"Пользователь {user.id} запустил /start")

    role = await get_user_role(user.id)
    logger.info(f"Загружена роль из БД: {role}")  # ✅ Проверка

    is_registered = role is not None

    welcome_text = WELCOME_MESSAGE
    if role:
        welcome_text += f"\n\n🔹 Вы зарегистрированы как: <b>{role}</b>"

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(is_registered=is_registered),
        parse_mode="HTML"
    )
    await state.clear()

@dp.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    await message.answer("🔐 Добро пожаловать в админ-панель!", reply_markup=get_admin_keyboard())

# --- Регистрация ---
@dp.callback_query(F.data == "start_registration")
async def start_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("✏️ Введите вашу фамилию, имя и отчество:")
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()

@dp.message(F.text, StateFilter(RegistrationStates.waiting_for_full_name))
async def process_full_name(message: Message, state: FSMContext) -> None:
    full_name = message.text.strip()
    if len(full_name.split()) < 2:
        await message.answer("❗ Введите полное ФИО (например: Иванов Иван Иванович).")
        return
    await state.update_data(full_name=full_name)
    await message.answer("🔢 Введите возраст:")
    await state.set_state(RegistrationStates.waiting_for_age)

@dp.message(F.text, StateFilter(RegistrationStates.waiting_for_age))
async def process_age(message: Message, state: FSMContext) -> None:
    age_text = message.text.strip()
    if not age_text.isdigit():
        await message.answer("❗ Введите возраст числом.")
        return
    age = int(age_text)
    if age < 1 or age > 120:
        await message.answer("❗ Введите реальный возраст (1–120).")
        return
    await state.update_data(age=age)
    await message.answer("🎯 Выберите роль:", reply_markup=get_role_keyboard())
    await state.set_state(RegistrationStates.waiting_for_role)

@dp.callback_query(F.data.startswith("role_"), StateFilter(RegistrationStates.waiting_for_role))
async def process_role(callback: CallbackQuery, state: FSMContext) -> None:
    role = "Взрослый" if callback.data == "role_adult" else "Ребёнок"
    await state.update_data(role=role)
    await callback.message.edit_text("📞 Введите ваш номер телефона:")
    await state.set_state(RegistrationStates.waiting_for_phone)
    await callback.answer()

@dp.message(F.text, StateFilter(RegistrationStates.waiting_for_phone))
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) < 10:
        await message.answer("❗ Введите корректный номер телефона.")
        return

    await state.update_data(phone=phone)
    data = await state.get_data()

    # 🔍 Логируем, что передаём
    logger.info(f"Сохраняем пользователя: {data}")

    await save_user(
        user_id=message.from_user.id,
        full_name=data['full_name'],
        age=data['age'],
        role=data['role'],  # ✅ Убедитесь, что тут правильная роль
        phone=phone
    )

    success_text = (
        f"🎉 <b>Регистрация завершена!</b>\n\n"
        f"👤 <b>ФИО:</b> {data['full_name']}\n"
        f"🎂 <b>Возраст:</b> {data['age']}\n"
        f"🆔 <b>Роль:</b> {data['role']}\n"  # ✅ Показываем правильную роль
        f"📱 <b>Телефон:</b> {phone}\n\n"
        "Теперь вы можете записаться на тренировку."
    )
    await message.answer(
        success_text,
        reply_markup=get_main_keyboard(is_registered=True),
        parse_mode="HTML"
    )
    await state.clear()

# --- Мой профиль ---
@dp.callback_query(F.data == "show_profile")
async def show_profile(callback: CallbackQuery, state: FSMContext) -> None:
    role = await get_user_role(callback.from_user.id)
    logger.info(f"Показываем профиль. Роль: {role}")  # ✅ Лог

    if not role:
        await callback.message.edit_text(
            "❌ Вы не зарегистрированы.",
            reply_markup=get_main_keyboard(is_registered=False)
        )
        await callback.answer()
        return

    pool = await create_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name, age, phone FROM users WHERE user_id = $1", callback.from_user.id)
    await pool.close()

    if not row:
        await callback.message.edit_text("❌ Не удалось загрузить данные профиля.")
        await callback.answer()
        return

    phone = row['phone'] or "не указан"

    profile_text = (
        "👤 <b>Мой профиль</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📌 <b>ФИО:</b> {row['full_name']}\n"
        f"🎂 <b>Возраст:</b> {row['age']}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        f"🎯 <b>Роль:</b> {role}\n\n"  # ✅ Правильная роль
        "Вы зарегистрированы в школе плавания <b>mariaswimpro</b>!"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(profile_text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# --- Расписание ---
@dp.callback_query(F.data == "show_schedule")
async def show_schedule(callback: CallbackQuery, state: FSMContext) -> None:
    role = await get_user_role(callback.from_user.id)
    if not role:
        await callback.message.edit_text("⚠️ Вы не зарегистрированы.")
        await callback.answer()
        return
    text = ADULT_SCHEDULE if role == "Взрослый" else CHILD_SCHEDULE

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# --- Прайс-лист ---
@dp.callback_query(F.data == "show_pricelist")
async def show_pricelist(callback: CallbackQuery, state: FSMContext) -> None:
    role = await get_user_role(callback.from_user.id)
    if not role:
        await callback.message.edit_text("⚠️ Сначала пройдите регистрацию.")
        await callback.answer()
        return

    text = await format_pricelist_for_children() if role == "Ребёнок" else await format_pricelist_for_adults()

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(text, reply_markup=markup)
    await callback.answer()

# --- Справки ---
@dp.callback_query(F.data == "show_requirements")
async def show_requirements(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(MEDICAL_REQUIREMENTS, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# --- Адреса ---
@dp.callback_query(F.data == "show_contacts")
async def show_addresses(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(CONTACTS_TEXT, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# --- Тренерский состав ---
@dp.callback_query(F.data == "show_coaches")
async def show_coaches(callback: CallbackQuery) -> None:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(COACHES_TEXT, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

# --- Запись на тренировку ---
@dp.callback_query(F.data == "register_training")
async def choose_training(callback: CallbackQuery, state: FSMContext) -> None:
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

# --- Выбор бассейна для взрослых ---
@dp.callback_query(F.data.startswith("adult_pool_"))
async def choose_adult_pool(callback: CallbackQuery, state: FSMContext) -> None:
    pool_key = callback.data.replace("adult_pool_", "")  # admiralteysky или dvvs
    await state.update_data(selected_pool=pool_key)
    keyboard = get_adult_schedule_keyboard(pool_key)
    pool_name = "Адмиралтейский" if pool_key == "admiralteysky" else "ДВВС"
    text = f"🏊‍♂️ <b>Выберите время тренировки</b>\n\n📍 Бассейн: {pool_name}"
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state("choosing_time")
    await callback.answer()

@dp.callback_query(F.data.startswith("pool_"))
async def choose_child_pool(callback: CallbackQuery, state: FSMContext) -> None:
    pool_key = callback.data.split("_", 1)[1]  # a_fitnes, dvvs
    await state.update_data(selected_pool=pool_key)
    keyboard = get_child_schedule_keyboard(pool_key)
    text = f"🧒 <b>Выберите время тренировки</b>\n\n📍 Бассейн: {pool_key.upper()}"
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await state.set_state("choosing_time")
    await callback.answer()

# --- Показать абонементы после выбора времени ---
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

    # Группируем и удаляем дубликаты по session_count внутри каждой группы
    grouped = {}
    for p in prices:
        service_type = p['service_type']
        duration = p['duration'] or '45 мин'
        key = f"{service_type}_{duration}"
        
        if key not in grouped:
            grouped[key] = {}
        
        # Используем session_count как ключ для удаления дубликатов
        grouped[key][p['session_count']] = p

    builder = InlineKeyboardBuilder()
    for key, items_dict in grouped.items():
        # Берем первую запись для получения service_type и duration
        first_item = next(iter(items_dict.values()))
        service_ru = SERVICE_TYPE_RU.get(first_item['service_type'], first_item['service_type'])
        duration = first_item['duration'] or '45 мин'
        
        builder.row(InlineKeyboardButton(
            text=f"📌 {service_ru} ({duration})",
            callback_data="header"
        ))
        
        # Сортируем по количеству тренировок и выводим без дубликатов
        for session_count in sorted(items_dict.keys()):
            p = items_dict[session_count]
            word = "тренировка" if p['session_count'] == 1 else "тренировки" if p['session_count'] in (2,3,4) else "тренировок"
            builder.button(
                text=f"🎟 {p['session_count']} {word} — {p['price']} ₽",
                callback_data=f"price_{p['id']}"
            )
        builder.adjust(1)

    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="register_training"))
    await state.update_data(selected_time_slot=slot, selected_time_text=time_text)
    await callback.message.edit_text(
        f"🏊‍♂️ <b>Выберите абонемент</b>\n\n⏰ <b>Время:</b> {time_text}\n🎯 <b>Роль:</b> {role}\n\nВыберите количество тренировок:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )
    await callback.answer()

# --- Сохранение записи с выбранной ценой ---
@dp.callback_query(F.data.startswith("price_"))
async def finalize_registration(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if 'selected_time_slot' not in data or 'selected_time_text' not in data:
        await callback.message.edit_text(
            "❌ Произошла ошибка: данные о времени утеряны.\nПожалуйста, начните запись заново.",
            reply_markup=InlineKeyboardBuilder().add(
                InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main")
            ).as_markup()
        )
        await state.clear()
        await callback.answer()
        return

    price_id = int(callback.data.split("_", 1)[1])
    slot = data['selected_time_slot']
    time_text = data['selected_time_text']
    user_id = callback.from_user.id

    # ✅ Берём роль из state (на момент записи)
    role = data.get('role')  # Должно быть "Взрослый"
    if not role:
        role = await get_user_role(user_id)  # Резервный вариант

    pool = await create_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT full_name FROM users WHERE user_id = $1", user_id)
        price_row = await conn.fetchrow("SELECT * FROM prices WHERE id = $1", price_id)
    await pool.close()

    if not row or not price_row:
        await callback.message.edit_text("❌ Ошибка загрузки данных.")
        await state.clear()
        await callback.answer()
        return

    full_name = row['full_name']
    session_count = price_row['session_count']
    price = price_row['price']

    await save_registration(user_id, full_name, role, time_text, session_count, price)

    word = "тренировка" if session_count == 1 else "тренировки" if session_count in (2,3,4) else "тренировок"
    price_text = f"{price:,} ₽".replace(",", " ")
    success_text = (
        "✅ <b>Вы успешно записаны!</b>\n\n"
        f"👤 <b>ФИО:</b> {full_name}\n"
        f"🎯 <b>Роль:</b> {role}\n"
        f"⏰ <b>Время:</b> {time_text}\n"
        f"🎟 <b>Абонемент:</b> {session_count} {word}\n"
        f"💰 <b>Цена:</b> {price_text}\n\n"
        "📞 При необходимости изменения — свяжитесь с администратором: +7 917 899 5088"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(success_text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()
    await state.clear()

# --- Админ-панель ---
@dp.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery, state: FSMContext) -> None:
    stats = await get_user_stats()
    text = (
        "📊 <b>Статистика пользователей</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Всего: <b>{stats['total']}</b>\n"
        f"🏊‍♂️ Взрослых: <b>{stats['adults']}</b>\n"
        f"👶 Детей: <b>{stats['children']}</b>"
    )
    if callback.message.text != text:
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "admin_users")
async def show_all_users(callback: CallbackQuery, state: FSMContext) -> None:
    users = await get_all_users()
    if not users:
        text = "📭 Нет зарегистрированных пользователей."
    else:
        text = "📋 <b>Все пользователи</b>\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for u in users:
            phone = u['phone'] or "не указан"
            text += (
                f"👤 <b>{u['full_name']}</b>\n"
                f"🔢 ID: <code>{u['user_id']}</code>\n"
                f"🎂 Возраст: {u['age']}\n"
                f"🎯 Роль: {u['role']}\n"
                f"📱 Телефон: {phone}\n"
                f"📅 {u['registered_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
            )
    if callback.message.text != text:
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "admin_finances")
async def show_finances(callback: CallbackQuery, state: FSMContext) -> None:
    report = await get_financial_report()
    text = (
        "💵 <b>Финансовый отчёт</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💸 Общий доход: <b>{report['total_revenue']} ₽</b>\n"
        f"🎫 Активных абонементов: <b>{report['active_subscriptions']}</b>\n\n"
        "ℹ️ Интеграция с оплатами будет добавлена позже."
    )
    if callback.message.text != text:
        await callback.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")
    await callback.answer()

# --- Редактирование прайса ---
@dp.callback_query(F.data == "edit_price_menu")
async def edit_price_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("Выберите категорию:", reply_markup=get_edit_price_category_keyboard())
    await callback.answer()
    
    
@dp.callback_query(F.data == "show_my_registrations")
async def show_my_registrations(callback: CallbackQuery) -> None:
    user_id = callback.from_user.id

    # 🔁 Берём роль из users, а не из registrations
    current_role = await get_user_role(user_id)
    if not current_role:
        text = "❌ Вы не зарегистрированы."
        markup = get_main_keyboard(is_registered=False)
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()
        return

    # 🔹 Берём запись из registrations
    registration = await get_user_registration(user_id)

    if not registration:
        text = (
            "📭 <b>Вы пока никуда не записаны.</b>\n\n"
            "Нажмите «Записаться», чтобы выбрать время и занятие."
        )
    else:
        # ✅ Используем актуальную роль из users, но данные из registrations
        time_text = registration['training_time']
        session_count = registration['session_count']
        price = registration['price']
        full_name = registration['full_name']

        word = "тренировка" if session_count == 1 else "тренировки" if session_count in (2,3,4) else "тренировок"
        price_text = f"{price:,} ₽".replace(",", " ")

        text = (
            "📋 <b>Ваши записи</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>ФИО:</b> {full_name}\n"
            f"🎯 <b>Роль:</b> {current_role}\n"  # ✅ Только из users
            f"⏰ <b>Время:</b> {time_text}\n"
            f"🎟 <b>Абонемент:</b> {session_count} {word}\n"
            f"💰 <b>Цена:</b> {price_text}\n\n"
            "Спасибо, что занимаетесь с нами! 🏊‍♂️"
        )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data.startswith("edit_prices_"))
async def show_prices_to_edit(callback: CallbackQuery, state: FSMContext) -> None:
    category_key = "adult" if "adult" in callback.data else "child"
    category_name = CATEGORY_RU[category_key]

    prices = await load_prices()
    prices = [p for p in prices if p['category'] == category_key]

    if not prices:
        text = f"📭 Нет цен для <b>{category_name}</b>."
    else:
        text = f"🔧 <b>Редактирование цен — {category_name}</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Удаляем дубликаты по service_type + duration + session_count
        unique_prices = {}
        for p in prices:
            key = f"{p['service_type']}_{p['duration'] or ''}_{p['session_count']}"
            unique_prices[key] = p

        # Группируем по service_type для отображения
        grouped = {}
        for p in unique_prices.values():
            service_ru = SERVICE_TYPE_RU.get(p['service_type'], p['service_type'])
            if service_ru not in grouped:
                grouped[service_ru] = []
            grouped[service_ru].append(p)

        for service_ru, items in grouped.items():
            text += f"📌 <b>{service_ru}</b>\n"
            for p in items:
                duration = f" ({p['duration']})" if p['duration'] else ""
                count = p['session_count']
                word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
                text += f"  • {count} {word}{duration} — <b>{p['price']} ₽</b>\n"
            text += "\n"

    # Создаем кнопки только для уникальных записей
    buttons = []
    unique_buttons = set()  # Для отслеживания дубликатов кнопок
    
    for p in prices:
        key = f"{p['service_type']}_{p['duration'] or ''}_{p['session_count']}"
        if key not in unique_buttons:
            unique_buttons.add(key)
            
            duration_str = p['duration'] or ''
            callback_data = f"edit_price:{category_key}:{p['service_type']}:{duration_str}:{p['session_count']}"
            service_ru = SERVICE_TYPE_RU.get(p['service_type'], p['service_type'])
            
            duration_text = f" ({p['duration']})" if p['duration'] else ""
            count = p['session_count']
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            
            buttons.append([
                InlineKeyboardButton(
                    text=f"✏️ {service_ru}{duration_text} - {count} {word}",
                    callback_data=callback_data
                )
            ])

    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

async def get_current_price(category: str, service_type: str, duration: str, session_count: int) -> int:
    """
    Получить текущую цену для указанных параметров
    """
    pool = await create_pool()
    async with pool.acquire() as conn:
        # Обрабатываем NULL значение duration
        clean_duration = duration if duration is not None else ''
        
        price = await conn.fetchval('''
            SELECT price FROM prices 
            WHERE category = $1 
            AND service_type = $2 
            AND COALESCE(duration, '') = COALESCE($3, '')
            AND session_count = $4
        ''', category, service_type, duration, session_count)
    
    await pool.close()
    return price if price is not None else 0

@dp.callback_query(F.data.startswith("edit_price:"))
async def prompt_new_price(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":", 5)
    if len(parts) != 5:
        await callback.answer("❌ Ошибка: неверный формат данных.")
        return

    _, category_key, service_type, duration_str, session_count_str = parts
    try:
        session_count = int(session_count_str)
    except ValueError:
        await callback.answer("❌ Ошибка: количество тренировок должно быть числом.")
        return

    duration = duration_str if duration_str else None

    # Получаем текущую цену из базы данных
    current_price = await get_current_price(category_key, service_type, duration, session_count)
    
    category_name = CATEGORY_RU[category_key]
    service_ru = SERVICE_TYPE_RU.get(service_type, service_type)
    duration_text = f" ({duration_str})" if duration_str else ""
    
    edit_text = (
        f"🔧 <b>Редактирование цены</b>\n\n"
        f"🎯 Категория: <b>{category_name}</b>\n"
        f"📋 Услуга: <b>{service_ru}</b>\n"
        f"⏱️ Длительность: <b>{duration_text.strip() or 'не указана'}</b>\n"
        f"🔢 Количество: <b>{session_count}</b>\n"
        f"💰 Нынешняя цена: <b>{current_price} ₽</b>\n\n"
        f"💵 Введите новую цену в рублях:"
    ).replace(",", " ")

    await callback.message.edit_text(edit_text, parse_mode="HTML")
    await callback.answer()

    await state.update_data(
        edit_price_category=category_key,
        edit_price_service_type=service_type,
        edit_price_duration=duration,
        edit_price_session_count=session_count
    )

    await state.set_state(PriceEditStates.waiting_for_price)

@dp.message(F.text.isdigit(), StateFilter(PriceEditStates.waiting_for_price))
async def update_price_value(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    category = data['edit_price_category']
    service_type = data['edit_price_service_type']
    duration = data['edit_price_duration']
    session_count = data['edit_price_session_count']
    new_price = int(message.text)

    clean_duration = duration if duration is not None else ''

    await update_price(category, service_type, clean_duration, session_count, new_price)

    category_name = CATEGORY_RU[category]
    service_ru = SERVICE_TYPE_RU.get(service_type, service_type)

    await message.answer(
        f"✅ Цена успешно обновлена!\n\n"
        f"🎯 Категория: {category_name}\n"
        f"📋 Услуга: {service_ru}\n"
        f"⏱ Длительность: {duration or 'не указана'}\n"
        f"🔢 Количество: {session_count}\n"
        f"💰 Новая цена: <b>{new_price:,} ₽</b>".replace(",", " "),
        parse_mode="HTML"
    )

    await message.answer("🔐 Админ-панель:", reply_markup=get_admin_keyboard())
    await state.clear()

# --- Сертификаты ---
@dp.callback_query(F.data == "show_certificates")
async def show_certificates(callback: CallbackQuery) -> None:
    text = (
        "🎁 <b>Подарочный сертификат</b>\n\n"
        "Хотите подарить близкому человеку здоровье и радость плавания?\n\n"
        "📞 <b>Позвоните по номеру и закажите сертификат!</b>\n"
        "<code>+7(917)855-53-88</code>\n\n"
        "Скидка 10%\n"
        "Подарок\n"
    )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "admin_back")
async def back_to_admin(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text("🔐 Админ-панель:", reply_markup=get_admin_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    role = await get_user_role(callback.from_user.id)
    is_registered = role is not None

    welcome_text = WELCOME_MESSAGE
    if role:
        welcome_text += f"\n\n🔹 Вы зарегистрированы как: <b>{role}</b>"

    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_keyboard(is_registered=is_registered),
        parse_mode="HTML"
    )
    await callback.answer()
    await state.clear()

# --- Админ: кто записался ---
@dp.callback_query(F.data == "admin_registrations")
async def show_registrations(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ У вас нет доступа.")
        return

    registrations = await get_all_registrations()
    if not registrations:
        text = "📭 Нет записавшихся пользователей."
    else:
        text = "👥 <b>Кто записался на тренировки</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for r in registrations:
            phone = r['phone'] or "не указан"
            word = "тренировка" if r['session_count'] == 1 else "тренировки" if r['session_count'] in (2,3,4) else "тренировок"
            text += (
                f"👤 <b>{r['full_name']}</b>\n"
                f"🔢 ID: <code>{r['user_id']}</code>\n"
                f"🎂 Возраст: {r['age']}\n"
                f"🎯 Роль: {r['role']}\n"
                f"⏰ Время: {r['training_time']}\n"
                f"🎟 Абонемент: {r['session_count']} {word}\n"
                f"💰 Цена: <b>{r['price']} ₽</b>\n"
                f"📱 Телефон: {phone}\n"
                f"📅 {r['registered_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
            )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_main"))
    markup = builder.as_markup()

    await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "open_shop")
async def open_shop(callback: CallbackQuery) -> None:
    shop_text = (
        "🛍 <b>Добро пожаловать в наш магазин!</b>\n\n"
        "Здесь вы найдёте всё необходимое для занятий плаванием:\n\n"
        "• Купальники и гидрокостюмы\n"
        "• Очки для плавания\n"
        "• Шапочки и ласты\n"
        "• Носки и перчатки для тренировок\n"
        "• Спортивные сумки и аксессуары\n\n"
        "Все товары проверены тренерами и учениками.\n"
        "Качество, комфорт и стиль — для каждого уровня подготовки!\n\n"
        "👉 Нажмите кнопку ниже, чтобы перейти:"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Перейти в магазин", url="https://t.me/swimthings")
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    builder.adjust(1)
    markup = builder.as_markup()

    await callback.message.edit_text(shop_text, reply_markup=markup, parse_mode="HTML")
    await callback.answer()