# keyboards.py
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_keyboard(is_registered: bool):
    builder = InlineKeyboardBuilder()
    if is_registered:
        builder.button(text="🖌️ Записаться", callback_data="register_training")
        builder.button(text="📅 Расписание", callback_data="show_schedule")
        builder.button(text="💰 Прайс-лист", callback_data="show_pricelist")
        builder.button(text="📍 Адреса", callback_data="show_contacts")
        builder.button(text="👨‍🏫 Контакты", callback_data="show_coaches")
        builder.button(text="📋 Мои записи", callback_data="show_my_registrations")
        builder.button(text="🎁 Сертификаты", callback_data="show_certificates")
        builder.button(text="🛍 Магазин", callback_data="open_shop")
        builder.button(text="📄 Мой профиль", callback_data="show_profile")
        builder.button(text="❓ Справки", callback_data="show_requirements")
    else:
        builder.button(text="✅ Регистрация", callback_data="start_registration")
    builder.adjust(1)
    return builder.as_markup()


def get_role_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍🦰 Взрослый", callback_data="role_adult")
    builder.button(text="👶 Ребёнок", callback_data="role_child")
    builder.adjust(1)
    return builder.as_markup()


def get_child_pool_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🏊 А-Фитнес", callback_data="pool_a_fitnes")
    builder.button(text="🏊 ДВВС", callback_data="pool_dvvs")
    builder.button(text="🏊 Адмиралтейский", callback_data="pool_admiralteysky")
    builder.button(text="🏊 Желанные дети", callback_data="pool_zhelannye")
    builder.button(text="🏊 Ватан", callback_data="pool_vatan")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_adult_pool_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📍 Адмиралтейский (ул. 1 Мая, д. 5)",
        callback_data="adult_pool_admiralteysky"
    )
    builder.button(
        text="📍 ДВВС (Сибгат Хакима, 70)",
        callback_data="adult_pool_dvvs"
    )
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()


def get_adult_schedule_keyboard(pool_key: str):
    builder = InlineKeyboardBuilder()

    if pool_key == "admiralteysky":
        times = [
            ("Пн/Пт, 20:00", "adult_admiralteysky_mf_2000"),
        ]
    elif pool_key == "dvvs":
        times = [
            ("Ср, 20:15", "adult_dvvs_wed_2015"),
        ]
    else:
        times = []

    for text, cb in times:
        builder.button(text=f"🏊‍♂️ {text}", callback_data=cb)

    builder.button(text="🔙 Назад", callback_data="register_training")
    builder.adjust(1)
    return builder.as_markup()


def get_child_schedule_keyboard(pool_key: str):
    """
    Расписание для детей по выбранному бассейну
    """
    builder = InlineKeyboardBuilder()

    if pool_key == "a_fitnes":
        # Групповые занятия
        times = [
            ("Вт/Чт, 15:45", "child_a_fitnes_tt_1545"),
            ("Сб, 14:15", "child_a_fitnes_sa_1415"),
            ("Сб, 15:00", "child_a_fitnes_sa_1500"),
            ("Пн/Пт, 15:00", "child_a_fitnes_mf_1500"),
            ("Пн/Пт, 15:45", "child_a_fitnes_mf_1545"),
            ("Ср, 15:00", "child_a_fitnes_wed_1500"),
            ("Ср, 15:45", "child_a_fitnes_wed_1545"),
            ("Вт/Пт, 9:45", "child_a_fitnes_mf_0945"),
        ]
        # Мини-группы
        mini_times = [
            ("Вт/Чт, 16:30", "child_mini_a_fitnes_tt_1630"),
            ("Вт/Чт, 20:15", "child_mini_a_fitnes_tt_2015"),
            ("Пн/Пт, 20:15", "child_mini_a_fitnes_mf_2015"),
            ("Ср, 20:15", "child_mini_a_fitnes_wed_2015"),
        ]

        # Добавляем обычные группы
        for text, cb in times:
            builder.button(text=f"🧒 Группа: {text}", callback_data=cb)

        # Добавляем заголовок "Мини-группы"
        builder.button(text="✨ Мини-группы (3-4 чел.)", callback_data="mini_header")

        # Добавляем мини-группы
        for text, cb in mini_times:
            builder.button(text=f"🧒 Мини: {text}", callback_data=cb)

    elif pool_key == "dvvs":
        times = [
            ("Ср, 18:45", "child_dvvs_wed_1845"),
            ("Ср, 19:30", "child_dvvs_wed_1930"),
            ("Ср, 20:15", "child_dvvs_wed_2015"),
        ]
        for text, cb in times:
            builder.button(text=f"🧒 {text}", callback_data=cb)

    elif pool_key == "admiralteysky":
        times = [
            ("Пн/Пт, 15:00", "child_admiralteysky_mf_1500"),
        ]
        for text, cb in times:
            builder.button(text=f"🧒 {text}", callback_data=cb)

    elif pool_key == "zhelannye":
        times = [
            ("Сб, 10:00", "child_zhelannye_sa_1000"),
            ("Вс, 11:00", "child_zhelannye_su_1100"),
        ]
        for text, cb in times:
            builder.button(text=f"🧒 {text}", callback_data=cb)

    elif pool_key == "vatan":
        times = [
            ("Пн/Ср, 17:00", "child_vatan_mw_1700"),
            ("Вт/Чт, 17:00", "child_vatan_tt_1700"),
        ]
        for text, cb in times:
            builder.button(text=f"🧒 {text}", callback_data=cb)

    # Общая кнопка "Назад"
    builder.button(text="🔙 Назад", callback_data="register_training")

    # Выравниваем: по одной кнопке в строке
    builder.adjust(1)
    return builder.as_markup()


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
    builder.button(text="🔙 Назад", callback_data="admin_back")
    builder.adjust(1)
    return builder.as_markup()


def get_shop_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Перейти в магазин", url="https://t.me/swimthings")
    builder.button(text="🏠 В главное меню", callback_data="back_to_main")
    builder.adjust(1)
    return builder