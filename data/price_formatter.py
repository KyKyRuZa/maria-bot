from database.prices import load_prices

def _get_training_word(count: int) -> str:
    if count == 1:
        return "тренировка"
    elif count in (2, 3, 4):
        return "тренировки"
    else:
        return "тренировок"

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
            word = _get_training_word(count)
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
            word = _get_training_word(count)
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"
    
    personal_30 = [p for p in prices if p['service_type'] == 'personal' and p['duration'] == '30 мин']
    if personal_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in personal_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = _get_training_word(count)
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
            word = _get_training_word(count)
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"
    
    split_30 = [p for p in prices if p['service_type'] == 'split' and p['duration'] == '30 мин']
    if split_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in split_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = _get_training_word(count)
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
            word = _get_training_word(count)
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
            word = _get_training_word(count)
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
            word = _get_training_word(count)
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"
    
    personal_30 = [p for p in prices if p['service_type'] == 'personal' and p['duration'] == '30 мин']
    if personal_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in personal_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = _get_training_word(count)
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
            word = _get_training_word(count)
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"
    
    split_30 = [p for p in prices if p['service_type'] == 'split' and p['duration'] == '30 мин']
    if split_30:
        text += "30 мин:\n"
        unique = {p['session_count']: p for p in split_30}
        for count in sorted(unique.keys()):
            p = unique[count]
            word = _get_training_word(count)
            text += f"{count} {word} - {p['price']} руб\n"
        text += "\n"
    
    text += "📞 Запись и консультация: +7(917)-855-53-88"
    return text