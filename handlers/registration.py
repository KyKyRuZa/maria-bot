from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import dp
from database.users import save_user, get_user_role
from keyboards.registration import get_role_keyboard
from keyboards.main_menu import get_main_keyboard
import logging

logger = logging.getLogger(__name__)

class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_age = State()
    waiting_for_role = State()
    waiting_for_phone = State()

@dp.callback_query(F.data == "start_registration")
async def start_registration(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✏️ Введите вашу фамилию, имя и отчество:")
    await state.set_state(RegistrationStates.waiting_for_full_name)
    await callback.answer()

@dp.message(F.text, RegistrationStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if len(full_name.split()) < 2:
        await message.answer("❗ Введите полное ФИО (например: Иванов Иван Иванович).")
        return
    await state.update_data(full_name=full_name)
    await message.answer("🔢 Введите возраст:")
    await state.set_state(RegistrationStates.waiting_for_age)

@dp.message(F.text, RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
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

@dp.callback_query(F.data.startswith("role_"), RegistrationStates.waiting_for_role)
async def process_role(callback: CallbackQuery, state: FSMContext):
    role = "Взрослый" if callback.data == "role_adult" else "Ребёнок"
    await state.update_data(role=role)
    await callback.message.edit_text("📞 Введите ваш номер телефона:")
    await state.set_state(RegistrationStates.waiting_for_phone)
    await callback.answer()

@dp.message(F.text, RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) < 10:
        await message.answer("❗ Введите корректный номер телефона.")
        return
    await state.update_data(phone=phone)
    data = await state.get_data()
    await save_user(
        user_id=message.from_user.id,
        full_name=data['full_name'],
        age=data['age'],
        role=data['role'],
        phone=phone
    )
    success_text = (
        f"🎉 <b>Регистрация завершена!</b>\n"
        f"👤 <b>ФИО:</b> {data['full_name']}\n"
        f"🎂 <b>Возраст:</b> {data['age']}\n"
        f"🆔 <b>Роль:</b> {data['role']}\n"
        f"📱 <b>Телефон:</b> {phone}\n"
        "Теперь вы можете записаться на тренировку."
    )
    await message.answer(success_text, reply_markup=get_main_keyboard(is_registered=True), parse_mode="HTML")
    await state.clear()