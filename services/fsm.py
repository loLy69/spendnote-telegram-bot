from aiogram.fsm.state import StatesGroup, State


class AddPurchaseStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_clear_confirmation = State()
