from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_age = State()
    waiting_for_role = State()
    waiting_for_phone = State()

class PriceEditStates(StatesGroup):
    waiting_for_price = State()