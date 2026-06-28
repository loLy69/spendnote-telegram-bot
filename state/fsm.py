from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    """Основные состояния пользователя"""
    browsing = State()  # Просмотр меню
    viewing_product = State()  # Просмотр товара


class CartState(StatesGroup):
    """Состояния при работе с корзиной"""
    in_cart = State()  # В корзине


class CheckoutState(StatesGroup):
    """Состояния оформления заказа"""
    checkout = State()  # Процесс оформления


class AddItemState(StatesGroup):
    """Добавление покупки вручную"""
    waiting_for_name = State()
    waiting_for_price = State()
    waiting_for_category = State()
    waiting_for_clear_confirmation = State()
