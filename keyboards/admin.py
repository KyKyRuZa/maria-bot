from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="📋 Все пользователи", callback_data="admin_users")
    builder.button(text="👥 Кто записался", callback_data="admin_registrations")
    builder.button(text="✏️ Редактировать прайс", callback_data="edit_price_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_edit_price_category_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍🦰 Взрослые", callback_data="edit_prices_adult")
    builder.button(text="👶 Дети", callback_data="edit_prices_child")
    builder.button(text="🔙 Назад в админ-панель", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()

def get_pagination_keyboard(current_page: int, total_pages: int, back_callback: str = "admin_back", page_prefix: str = "admin_users_page_"):
    """
    Создает универсальную панель навигации для пагинации
    """
    builder = InlineKeyboardBuilder()
    
    if total_pages > 1:
        if current_page > 1:
            builder.button(text="⬅️ Назад", callback_data=f"{page_prefix}{current_page - 1}")
        if current_page < total_pages:
            builder.button(text="➡️ Вперёд", callback_data=f"{page_prefix}{current_page + 1}")
    
    if builder.buttons:
        builder.row()
    
    if back_callback == "admin_back":
        builder.button(text="🔙 Меню", callback_data=back_callback)
    else:
        builder.button(text="🔙 Назад", callback_data=back_callback)
    
    return builder.as_markup()