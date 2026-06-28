"""
Сервис для работы с товарами и каталогом
"""

from data.products import get_product, get_products_by_category, get_all_products, PRODUCT_CATEGORIES


class ProductService:
    """Бизнес-логика товаров"""
    
    @staticmethod
    def get_product(product_id: str) -> dict | None:
        """Получить товар по ID"""
        return get_product(product_id)
    
    @staticmethod
    def get_products_by_category(category: str) -> list[dict]:
        """Получить товары по категории"""
        return get_products_by_category(category)
    
    @staticmethod
    def get_all_products() -> list[dict]:
        """Получить все товары"""
        return get_all_products()
    
    @staticmethod
    def get_categories() -> dict[str, str]:
        """Получить все категории"""
        return PRODUCT_CATEGORIES.copy()
    
    @staticmethod
    def format_product(product: dict) -> str:
        """Отформатировать товар для вывода"""
        return (
            f"{product['emoji']} {product['name']}\n"
            f"💰 {product['price']} ₽\n"
            f"{product['description']}"
        )


# Глобальный экземпляр
product_service = ProductService()
