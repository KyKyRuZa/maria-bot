from .main_menu import get_main_keyboard
from .registration import get_role_keyboard
from .training_selection import (
    get_adult_pool_keyboard,
    get_child_pool_keyboard,
    get_adult_schedule_keyboard,
    get_child_schedule_keyboard
)
from .admin import get_admin_keyboard, get_edit_price_category_keyboard

__all__ = [
    'get_main_keyboard',
    'get_role_keyboard',
    'get_adult_pool_keyboard',
    'get_child_pool_keyboard',
    'get_adult_schedule_keyboard',
    'get_child_schedule_keyboard',
    'get_admin_keyboard',
    'get_edit_price_category_keyboard'
]