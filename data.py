# data.py
from database import load_prices

WELCOME_MESSAGE = (
    "Здравствуйте!\n"
    "Вас приветствует школа плавания <b>mariaswimpro</b>! 🏊‍♀️"
)

MEDICAL_REQUIREMENTS = (
    "📋 <b>НЕОБХОДИМЫЕ СПРАВКИ ДЛЯ ЗАНЯТИЙ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "❗ <b>Обязательные справки:</b>\n"
    "• Соскоб на энтеробиоз\n"
    "• Анализ кала на яйца глист\n"
    "• Допуск от педиатра (дети) или терапевта (взрослые) к занятиям плаванием\n\n"
    "🚫 <b>ВАЖНО:</b>\n"
    "Без предоставления справок к занятиям <b>не допускаются</b>.\n\n"
    "ℹ️ Справки действуют 1 год."
)

ADULT_SCHEDULE = (
    "🏊‍♂️ <b>РАСПИСАНИЕ ДЛЯ ВЗРОСЛЫХ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "📍 <b>ДВВС</b> (Сибгат Хакима, 70)\n"
    "• Среда — 20:15\n\n"
    "📍 <b>Адмиралтейский</b> (ул. 1 Мая, д. 5)\n"
    "• Понедельник и Пятница — 20:00\n\n"
    "ℹ️ <i>Группы по 10–12 человек.</i>"
)

CHILD_SCHEDULE = (
    "👧👦 <b>РАСПИСАНИЕ ДЛЯ ДЕТЕЙ</b>\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "📍 <b>ДВВС</b> (Сибгат Хакима, 70)\n"
    "• Среда — 18:45 (группа 10–15 чел)\n"
    "• Среда — 19:30 (группа 10–15 чел)\n"
    "• Среда — 20:15 (группа 10–15 чел)\n\n"
    "📍 <b>Адмиралтейский</b> (ул. 1 Мая, д. 5)\n"
    "• Понедельник и Пятница — 15:00 (группа 10–15 чел)\n\n"
    "📍 <b>А-Фитнес</b> (Ибрагимова, 54)- глубокий бассейн\n"
    "📌 <b>Групповые занятия</b> (10–12 человек)\n"
    "• Вторник и Четверг — 15:45\n"
    "• Суббота — 14:15, 15:00\n"
    "• Понедельник и Пятница — 15:00, 15:45\n"
    "• Среда — 15:00, 15:45\n"
    "• Вторник и Пятница — 9:45\n\n"
    "📌 <b>Мини-группы</b> (3–4 человека)\n"
    "• Вторник и Четверг — 16:30, 20:15\n"
    "• Понедельник и Пятница — 20:15\n"
    "• Среда — 20:15\n\n"
    "📍 <b>Ватан</b> (Бондаренко 2)\n"
    "🚫 <i>Временно не работаем</i>\n\n"
    "📍 <b>Желанные дети</b> (Горсоветская 10)- малая ванна\n"
    "📅 <i>По предварительной записи</i>\n"
    "• Понедельник и Четверг\n"
    "📞 Запись по телефону: +7(917)-855-53-88\n\n"
    "ℹ️ <i>Все занятия проводятся под руководством опытных тренеров.</i>"
)

CONTACTS_TEXT = (
    "📍 <b>Адреса бассейнов:</b>\n\n"
    "1️⃣ <b>Дворец водных видов спорта</b>\n"
    "ул. Сибгат Хакима, 70\n\n"
    "2️⃣ <b>СК «Ватан»</b>\n"
    "ул. Бондаренко, 2\n\n"
    "3️⃣ <b>СК «А-Fitness»</b>\n"
    "ул. Ибрагимова, 54\n\n"
    "4️⃣ <b>Бассейн «Адмиралтейский»</b>\n"
    "ул. 1 мая, д. 5\n\n"
    "5️⃣ <b>Бассейн «Желанные дети»</b>\n"
    "ул. Горсоветская, 10"
)

COACHES_TEXT = (
    "👨‍🏫 <b>Тренерский состав:</b>\n\n"
    "📞 <b>+7(917)-855-53-88</b>\n"
    "Беляева Мария Геннадьевна\n\n"
    "📞 <b>+7(917)-396-83-10</b>\n"
    "Трофимов Кирилл Константинович\n\n"
    "📞 <b>+7(927)-472-17-12</b>\n"
    "Зайцева Ирина Анатольевна\n\n"
    "📞 <b>+7(917)-899-50-88</b>\n"
    "Администратор\n\n"
    
)


async def format_pricelist_for_adults() -> str:
    rows = await load_prices()
    prices = [r for r in rows if r['category'] == 'adult']

    text = "Прайс для взрослых\nВ группе:\n"

    # Групповые
    group = [p for p in prices if p['service_type'] == 'group']
    if group:
        unique = {p['session_count']: p for p in group}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    # Персональные
    text += "Персональные занятия:\n"
    personal_45 = [p for p in prices if p['service_type'] == 'personal' and p['duration'] == '45 мин']
    if personal_45:
        text += "45 мин:\n"
        unique = {p['session_count']: p for p in personal_45}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    personal_30 = [p for p in prices if p['service_type'] == 'personal' and p['duration'] == '30 мин']
    if personal_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in personal_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    # Сплит
    text += "Сплит – тренировки:\n"
    split_45 = [p for p in prices if p['service_type'] == 'split' and p['duration'] == '45 мин']
    if split_45:
        text += "45 мин:\n"
        unique = {p['session_count']: p for p in split_45}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    split_30 = [p for p in prices if p['service_type'] == 'split' and p['duration'] == '30 мин']
    if split_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in split_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    text += "📞 Запись и консультация: +7(917)-855-53-88"
    return text


async def format_pricelist_for_children() -> str:
    rows = await load_prices()
    prices = [r for r in rows if r['category'] == 'child']

    text = "Прайс для детей\n"

    # Групповые
    group = [p for p in prices if p['service_type'] == 'group']
    if group:
        text += "ГРУППОВЫЕ (10-12 человек) 45 мин:\n"
        unique = {p['session_count']: p for p in group}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    # Мини-группы
    mini = [p for p in prices if p['service_type'] == 'mini_group']
    if mini:
        text += "Мини группы (3-4 Чел):\n"
        text += "45 мин:\n"
        unique = {p['session_count']: p for p in mini}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    # Персональные
    text += "Персональные занятия:\n"
    personal_45 = [p for p in prices if p['service_type'] == 'personal' and p['duration'] == '45 мин']
    if personal_45:
        text += "45 мин:\n"
        unique = {p['session_count']: p for p in personal_45}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    personal_30 = [p for p in prices if p['service_type'] == 'personal' and p['duration'] == '30 мин']
    if personal_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in personal_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    # Сплит
    text += "Сплит – тренировки:\n"
    split_45 = [p for p in prices if p['service_type'] == 'split' and p['duration'] == '45 мин']
    if split_45:
        text += "45 мин:\n"
        unique = {p['session_count']: p for p in split_45}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    split_30 = [p for p in prices if p['service_type'] == 'split' and p['duration'] == '30 мин']
    if split_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in split_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = "тренировка" if count == 1 else "тренировки" if count in (2,3,4) else "тренировок"
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"

    text += "📞 Запись и консультация: +7(917)-855-53-88"
    return text