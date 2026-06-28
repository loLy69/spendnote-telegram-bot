import re
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ParsedPurchase:
    name: str
    price: Optional[int]
    category: Optional[str]
    raw_text: str


class PurchaseParser:
    CATEGORY_KEYWORDS = {
        'Одежда': ['одежда', 'одежды', 'одежду', 'одежку', 'одежки', 'одежка'],
        'Техника': ['техника', 'технику', 'технике', 'гаджет', 'гаджеты', 'телефон', 'ноутбук', 'планшет'],
        'Еда': ['еда', 'еды', 'еду', 'булка', 'булки', 'ресторан', 'кафе', 'продукты'],
        'Поездки': ['поездка', 'поездки', 'билет', 'билеты', 'такси', 'метро', 'самолет', 'поезд'],
        'Развлечения': ['развлечение', 'развлечения', 'кино', 'концерт', 'парк', 'игра', 'хобби'],
        'Быт': ['быт', 'хозяйство', 'сантехника', 'посуду', 'посуд', 'мыло', 'шампунь', 'уборка'],
        'Другое': ['другое', 'прочее', 'разное', 'misc'],
    }

    PRICE_REGEX = re.compile(r'(\d+(?:\s\d{3})*)')

    @classmethod
    def _match_category(cls, token: str) -> Optional[str]:
        normalized = token.lower().strip()
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if normalized == keyword.lower():
                    return category
        return None

    @classmethod
    def _find_price(cls, text: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        match = None
        for m in cls.PRICE_REGEX.finditer(text):
            match = m
        if not match:
            return None, None, None
        try:
            amount_str = match.group(1).replace(' ', '')
            return int(amount_str), match.start(), match.end()
        except ValueError:
            return None, None, None

    @classmethod
    def parse(cls, text: str) -> ParsedPurchase:
        cleaned = text.strip()
        if not cleaned:
            return ParsedPurchase(name='', price=None, category=None, raw_text=text)

        price, price_start, price_end = cls._find_price(cleaned)
        text_without_price = cleaned
        if price is not None and price_start is not None and price_end is not None:
            text_without_price = (cleaned[:price_start] + ' ' + cleaned[price_end:]).strip()

        tokens = [t for t in re.split(r'\s+', text_without_price) if t]
        if not tokens:
            return ParsedPurchase(name='', price=price, category=None, raw_text=text)

        category = None
        category_idx = -1
        for idx, token in enumerate(tokens):
            matched_cat = cls._match_category(token)
            if matched_cat:
                category = matched_cat
                category_idx = idx
                break

        name_tokens = [t for i, t in enumerate(tokens) if i != category_idx]
        name = ' '.join(name_tokens).strip()

        return ParsedPurchase(name=name or 'Товар', price=price, category=category, raw_text=text)

    @classmethod
    def detect_category(cls, text: str) -> Optional[str]:
        cleaned = text.strip()
        if not cleaned:
            return None
        tokens = [t for t in re.split(r'\s+', cleaned) if t]
        for token in tokens:
            category = cls._match_category(token)
            if category:
                return category
        return None
