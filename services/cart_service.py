"""
Сервис для работы с корзиной
Обрабатывает логику добавления, удаления, оформления заказа
"""

from state.storage import cart_storage
from data.products import get_product


class CartService:
    """Бизнес-логика корзины"""
    
    @staticmethod
    def add_product(user_id: int, product_id: str, qty: int = 1) -> tuple[bool, str]:
        """
        Добавить товар в корзину
        Returns: (success: bool, message: str)
        """
        product = get_product(product_id)
        if not product:
            return False, '❌ Товар не найден'
        
        cart_storage.add_to_cart(
            user_id,
            product_id=product['product_id'],
            name=product['name'],
            price=product['price'],
            qty=qty,
        )
        return True, f"✅ {product['name']} добавлен в корзину"
    
    @staticmethod
    def remove_product(user_id: int, product_id: str) -> tuple[bool, str]:
        """
        Удалить товар из корзины
        Returns: (success: bool, message: str)
        """
        product = get_product(product_id)
        if not product:
            return False, '❌ Товар не найден'
        
        if cart_storage.remove_from_cart(user_id, product_id):
            return True, f"✅ {product['name']} удален из корзины"
        return False, '❌ Товара не было в корзине'
    
    @staticmethod
    def update_quantity(user_id: int, product_id: str, qty: int) -> tuple[bool, str]:
        """
        Обновить количество товара
        Returns: (success: bool, message: str)
        """
        if qty <= 0:
            return CartService.remove_product(user_id, product_id)
        
        product = get_product(product_id)
        if not product:
            return False, '❌ Товар не найден'
        
        if cart_storage.update_quantity(user_id, product_id, qty):
            return True, f"✅ Количество {product['name']} обновлено: {qty} шт"
        return False, '❌ Ошибка обновления'
    
    @staticmethod
    def get_cart_items(user_id: int) -> list[dict]:
        """Получить содержимое корзины"""
        return cart_storage.get_cart(user_id)
    
    @staticmethod
    def get_cart_summary(user_id: int) -> dict:
        """Получить сводку по корзине"""
        items = cart_storage.get_cart(user_id)
        total = cart_storage.get_cart_total(user_id)
        count = cart_storage.get_cart_count(user_id)
        
        return {
            'items': items,
            'total': total,
            'count': count,
            'is_empty': len(items) == 0,
        }
    
    @staticmethod
    def clear_cart(user_id: int) -> str:
        """Очистить корзину"""
        cart_storage.clear_cart(user_id)
        return '✅ Корзина очищена'
    
    @staticmethod
    def checkout(user_id: int) -> tuple[bool, str, dict | None]:
        """
        Оформить заказ
        Returns: (success: bool, message: str, order_data: dict | None)
        """
        summary = CartService.get_cart_summary(user_id)
        
        if summary['is_empty']:
            return False, '❌ Корзина пуста', None
        
        order_data = {
            'user_id': user_id,
            'items': summary['items'],
            'total': summary['total'],
            'status': 'pending',
        }
        
        CartService.clear_cart(user_id)
        return True, f"✅ Заказ оформлен! Сумма: {summary['total']} ₽", order_data


# Глобальный экземпляр
cart_service = CartService()
