from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_keyboard(is_registered: bool):
    builder = InlineKeyboardBuilder()
    if is_registered:
        builder.button(text="🖌️ Записаться", callback_data="register_training")
        builder.button(text="📋 Мои записи", callback_data="show_my_registrations")
        
        builder.button(text="📅 Расписание", callback_data="show_schedule")
        builder.button(text="💰 Прайс-лист", callback_data="show_pricelist")
        builder.button(text="📍 Адреса", callback_data="show_contacts")
        builder.button(text="👨‍🏫 Контакты", callback_data="show_coaches")
        
        builder.button(text="🎁 Сертификаты", callback_data="show_certificates")
        builder.button(text="🛍 Магазин", callback_data="open_shop")
        builder.button(text="📄 Мой профиль", callback_data="show_profile")
        builder.button(text="❓ Справки", callback_data="show_requirements")
    else:
        builder.button(text="✅ Регистрация", callback_data="start_registration")
    builder.adjust(1)
    return builder.as_markup()