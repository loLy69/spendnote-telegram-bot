"""
Каталог товаров магазина
"""

PRODUCT_CATEGORIES = {
    'clothes': '👕 Одежда',
    'tech': '📱 Техника',
    'food': '🍔 Еда',
    'travel': '✈️ Поездки',
    'entertainment': '🎮 Развлечения',
    'home': '🏠 Быт',
}

products = [
    # Одежда
    {
        'product_id': 'shirt_001',
        'name': 'Футболка',
        'price': 1500,
        'category': 'clothes',
        'description': 'Комфортная хлопковая футболка',
        'emoji': '👕',
    },
    {
        'product_id': 'pants_001',
        'name': 'Джинсы',
        'price': 3500,
        'category': 'clothes',
        'description': 'Классические джинсы',
        'emoji': '👖',
    },
    {
        'product_id': 'socks_001',
        'name': 'Носки',
        'price': 300,
        'category': 'clothes',
        'description': 'Комплект носков (3 пары)',
        'emoji': '🧦',
    },
    
    # Техника
    {
        'product_id': 'phone_001',
        'name': 'Наушники',
        'price': 5000,
        'category': 'tech',
        'description': 'Беспроводные наушники',
        'emoji': '🎧',
    },
    {
        'product_id': 'charger_001',
        'name': 'Зарядка',
        'price': 2000,
        'category': 'tech',
        'description': 'Быстрая зарядка USB-C',
        'emoji': '🔌',
    },
    
    # Еда
    {
        'product_id': 'coffee_001',
        'name': 'Кофе',
        'price': 500,
        'category': 'food',
        'description': 'Арабика в зёрнах (250г)',
        'emoji': '☕',
    },
    {
        'product_id': 'chocolate_001',
        'name': 'Шоколад',
        'price': 200,
        'category': 'food',
        'description': 'Чёрный шоколад 70%',
        'emoji': '🍫',
    },
    
    # Поездки
    {
        'product_id': 'luggage_001',
        'name': 'Рюкзак',
        'price': 4000,
        'category': 'travel',
        'description': 'Туристический рюкзак 40л',
        'emoji': '🎒',
    },
    
    # Развлечения
    {
        'product_id': 'game_001',
        'name': 'Игра',
        'price': 1000,
        'category': 'entertainment',
        'description': 'Популярная компьютерная игра',
        'emoji': '🎮',
    },
    
    # Быт
    {
        'product_id': 'lamp_001',
        'name': 'Лампа',
        'price': 800,
        'category': 'home',
        'description': 'LED настольная лампа',
        'emoji': '💡',
    },
]


def get_product(product_id: str) -> dict | None:
    """Получить товар по ID"""
    for product in products:
        if product['product_id'] == product_id:
            return product
    return None


def get_products_by_category(category: str) -> list[dict]:
    """Получить товары по категории"""
    return [p for p in products if p['category'] == category]


def get_all_products() -> list[dict]:
    """Получить все товары"""
    return products.copy()
