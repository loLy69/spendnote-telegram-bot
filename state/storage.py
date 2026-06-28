"""
In-memory storage для корзины и состояния пользователя
Структура:
{
    userId: {
        items: [
            { product_id: str, name: str, price: int, qty: int },
            ...
        ]
    }
}
"""

from typing import Optional


class CartStorage:
    """Хранилище корзин пользователей"""
    
    def __init__(self):
        self.carts: dict[int, dict] = {}
    
    def _ensure_user(self, user_id: int) -> None:
        """Инициализировать корзину пользователя если её нет"""
        if user_id not in self.carts:
            self.carts[user_id] = {'items': []}
    
    def add_to_cart(self, user_id: int, product_id: str, name: str, price: int, qty: int = 1) -> None:
        """Добавить товар в корзину или увеличить количество"""
        self._ensure_user(user_id)
        
        # Проверить, есть ли такой товар
        for item in self.carts[user_id]['items']:
            if item['product_id'] == product_id:
                item['qty'] += qty
                return
        
        # Если нет, добавить новый
        self.carts[user_id]['items'].append({
            'product_id': product_id,
            'name': name,
            'price': price,
            'qty': qty,
        })
    
    def remove_from_cart(self, user_id: int, product_id: str) -> bool:
        """Удалить товар из корзины"""
        self._ensure_user(user_id)
        
        for i, item in enumerate(self.carts[user_id]['items']):
            if item['product_id'] == product_id:
                del self.carts[user_id]['items'][i]
                return True
        return False
    
    def update_quantity(self, user_id: int, product_id: str, qty: int) -> bool:
        """Обновить количество товара"""
        self._ensure_user(user_id)
        
        if qty <= 0:
            return self.remove_from_cart(user_id, product_id)
        
        for item in self.carts[user_id]['items']:
            if item['product_id'] == product_id:
                item['qty'] = qty
                return True
        return False
    
    def get_cart(self, user_id: int) -> list[dict]:
        """Получить содержимое корзины"""
        self._ensure_user(user_id)
        return self.carts[user_id]['items']
    
    def get_cart_total(self, user_id: int) -> int:
        """Получить общую сумму корзины"""
        self._ensure_user(user_id)
        return sum(item['price'] * item['qty'] for item in self.carts[user_id]['items'])
    
    def get_cart_count(self, user_id: int) -> int:
        """Получить количество товаров в корзине"""
        self._ensure_user(user_id)
        return sum(item['qty'] for item in self.carts[user_id]['items'])
    
    def clear_cart(self, user_id: int) -> None:
        """Очистить корзину"""
        self._ensure_user(user_id)
        self.carts[user_id]['items'] = []
    
    def is_empty(self, user_id: int) -> bool:
        """Проверить, пуста ли корзина"""
        self._ensure_user(user_id)
        return len(self.carts[user_id]['items']) == 0


# Глобальный экземпляр storage
cart_storage = CartStorage()
