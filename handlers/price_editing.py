from aiogram import F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import dp
from data.text_content import CATEGORY_RU, SERVICE_TYPE_RU
from database.prices import load_prices, update_price, get_current_price

class PriceEditStates(StatesGroup):
    waiting_for_price = State()

@dp.callback_query(F.data == "edit_price_menu")
async def edit_price_menu(callback: CallbackQuery):
    from keyboards.admin import get_edit_price_category_keyboard
    await callback.message.edit_text("Выберите категорию:", reply_markup=get_edit_price_category_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_prices_"))
async def show_prices_to_edit(callback: CallbackQuery):
    category_key = "adult" if "adult" in callback.data else "child"
    category_name = CATEGORY_RU[category_key]
    prices = await load_prices()
    prices = [p for p in prices if p['category'] == category_key]
    
    if not prices:
        text = f"📭 Нет цен для <b>{category_name}</b>."
    else:
        text = f"🔧 <b>Редактирование цен — {category_name}</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        unique_prices = {}
        for p in prices:
            key = f"{p['service_type']}_{p['duration'] or ''}_{p['session_count']}"
            unique_prices[key] = p
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
    
    # Создаем кнопки правильно
    buttons = []
    unique_buttons = set()
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
            
            # Используем InlineKeyboardButton вместо CallbackQuery.inline_keyboard
            buttons.append([
                InlineKeyboardButton(
                    text=f"✏️ {service_ru}{duration_text} - {count} {word}",
                    callback_data=callback_data
                )
            ])
    
    # Добавляем кнопку "Назад"
    buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_back")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_price:"))
async def prompt_new_price(callback: CallbackQuery, state: FSMContext):
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
    current_price = await get_current_price(category_key, service_type, duration, session_count)
    category_name = CATEGORY_RU[category_key]
    service_ru = SERVICE_TYPE_RU.get(service_type, service_type)
    duration_text = f" ({duration_str})" if duration_str else ""
    edit_text = (
        f"🔧 <b>Редактирование цены</b>\n"
        f"🎯 Категория: <b>{category_name}</b>\n"
        f"📋 Услуга: <b>{service_ru}</b>\n"
        f"⏱️ Длительность: <b>{duration_text.strip() or 'не указана'}</b>\n"
        f"🔢 Количество: <b>{session_count}</b>\n"
        f"💰 Нынешняя цена: <b>{current_price} ₽</b>\n"
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

@dp.message(F.text.isdigit(), PriceEditStates.waiting_for_price)
async def update_price_value(message: Message, state: FSMContext):
    data = await state.get_data()
    category = data['edit_price_category']
    service_type = data['edit_price_service_type']
    duration = data['edit_price_duration']
    session_count = data['edit_price_session_count']
    new_price = int(message.text)
    await update_price(category, service_type, duration, session_count, new_price)
    category_name = CATEGORY_RU[category]
    service_ru = SERVICE_TYPE_RU.get(service_type, service_type)
    await message.answer(
        f"✅ Цена успешно обновлена!\n"
        f"🎯 Категория: {category_name}\n"
        f"📋 Услуга: {service_ru}\n"
        f"⏱ Длительность: {duration or 'не указана'}\n"
        f"🔢 Количество: {session_count}\n"
        f"💰 Новая цена: <b>{new_price:,} ₽</b>".replace(",", " "),
        parse_mode="HTML"
    )
    from keyboards.admin import get_admin_keyboard
    await message.answer("🔐 Админ-панель:", reply_markup=get_admin_keyboard())
    await state.clear()