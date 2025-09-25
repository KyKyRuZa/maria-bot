from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_role_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍🦰 Взрослый", callback_data="role_adult")
    builder.button(text="👶 Ребёнок", callback_data="role_child")
    builder.adjust(1)
    return builder.as_markup()