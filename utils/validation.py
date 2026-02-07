import re
from typing import Union


def validate_user_id(user_id: Union[str, int]) -> int:
    try:
        user_id_int = int(user_id)
        if user_id_int <= 0:
            raise ValueError("user_id должен быть положительным целым числом")
        return user_id_int
    except (ValueError, TypeError):
        raise ValueError("user_id должен быть положительным целым числом")


def validate_full_name(full_name: str) -> str:
    if not isinstance(full_name, str):
        raise ValueError("full_name должен быть строкой")
    
    if not full_name.strip():
        raise ValueError("full_name не может быть пустым")
    
    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-\'\"]+$', full_name.strip()):
        raise ValueError("full_name содержит недопустимые символы")
    
    return full_name.strip()


def validate_age(age: Union[str, int]) -> int:
    try:
        age_int = int(age)
        if age_int < 1 or age_int > 120:
            raise ValueError("age должен быть в диапазоне от 1 до 120")
        return age_int
    except (ValueError, TypeError):
        raise ValueError("age должен быть числом в диапазоне от 1 до 120")


def validate_role(role: str) -> str:
    if not isinstance(role, str):
        raise ValueError("role должен быть строкой")
    
    if role not in ["Взрослый", "Ребёнок"]:
        raise ValueError("role должен быть 'Взрослый' или 'Ребёнок'")
    
    return role


def validate_phone(phone: str) -> str:
    if not isinstance(phone, str):
        raise ValueError("phone должен быть строкой")
    
    digits_only = re.sub(r'\D', '', phone)
    
    if len(digits_only) < 10:
        raise ValueError("phone должен содержать не менее 10 цифр")
    
    return phone


def validate_training_time(training_time: str) -> str:
    if not isinstance(training_time, str):
        raise ValueError("training_time должен быть строкой")
    
    if not training_time.strip():
        raise ValueError("training_time не может быть пустым")
    
    return training_time.strip()


def validate_session_count(session_count: Union[str, int]) -> int:
    try:
        session_count_int = int(session_count)
        if session_count_int <= 0:
            raise ValueError("session_count должен быть положительным целым числом")
        return session_count_int
    except (ValueError, TypeError):
        raise ValueError("session_count должен быть положительным целым числом")


def validate_price(price: Union[str, int]) -> int:
    try:
        price_int = int(price)
        if price_int < 0:
            raise ValueError("price не может быть отрицательным")
        return price_int
    except (ValueError, TypeError):
        raise ValueError("price должен быть неотрицательным целым числом")


def validate_category(category: str) -> str:
    if not isinstance(category, str):
        raise ValueError("category должен быть строкой")
    
    if category not in ["adult", "child"]:
        raise ValueError("category должен быть 'adult' или 'child'")
    
    return category


def validate_service_type(service_type: str) -> str:
    if not isinstance(service_type, str):
        raise ValueError("service_type должен быть строкой")
    
    if not re.match(r'^[a-zA-Z_]+$', service_type):
        raise ValueError("service_type содержит недопустимые символы")
    
    return service_type