from aiogram.fsm.state import State, StatesGroup


class AddPurchaseStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()


class SettingsStates(StatesGroup):
    waiting_for_budget = State()
    waiting_for_clear_confirmation = State()
