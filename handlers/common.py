from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import dp
from data.text_content import WELCOME_MESSAGE
from database.users import get_user_role
from keyboards.main_menu import get_main_keyboard

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    user = message.from_user
    role = await get_user_role(user.id)
    is_registered = role is not None
    welcome_text = WELCOME_MESSAGE
    if role:
        welcome_text += f"\n\n🔹 Вы зарегистрированы как: <b>{role}</b>"
    await message.answer(welcome_text, reply_markup=get_main_keyboard(is_registered=is_registered), parse_mode="HTML")
    await state.clear()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    role = await get_user_role(callback.from_user.id)
    is_registered = role is not None
    welcome_text = WELCOME_MESSAGE
    if role:
        welcome_text += f"\n\n🔹 Вы зарегистрированы как: <b>{role}</b>"
    await callback.message.edit_text(welcome_text, reply_markup=get_main_keyboard(is_registered=is_registered), parse_mode="HTML")
    await callback.answer()
    await state.clear()

    