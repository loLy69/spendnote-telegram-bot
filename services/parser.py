from __future__ import annotations

import re
from dataclasses import dataclass

from services.db import CATEGORIES, DEFAULT_CATEGORY, DEFAULT_PRIORITY, DEFAULT_STATUS, normalize_category


@dataclass(frozen=True)
class ParsedPurchase:
    name: str
    price: int | None
    category: str | None
    status: str
    priority: str
    note: str
    raw_text: str


class PurchaseParser:
    PRICE_REGEX = re.compile(r"(?<!\d)(\d{1,3}(?:[\s\u00A0]\d{3})*|\d+)(?:\s*(?:р|руб|₽))?(?!\d)", re.IGNORECASE)
    NOTE_REGEX = re.compile(r"(?:заметка|коммент|note)\s*:\s*(.+)$", re.IGNORECASE)

    STATUS_KEYWORDS = {
        "купил": "bought",
        "купила": "bought",
        "куплено": "bought",
        "оплатил": "bought",
        "оплачено": "bought",
        "хочу": "planned",
        "надо": "planned",
        "купить": "planned",
        "план": "planned",
        "отложить": "skipped",
        "потом": "skipped",
    }

    PRIORITY_KEYWORDS = {
        "важно": "high",
        "срочно": "high",
        "обязательно": "high",
        "must": "high",
        "неважно": "low",
        "когда-нибудь": "low",
    }

    @classmethod
    def parse(cls, text: str) -> ParsedPurchase:
        cleaned = " ".join((text or "").strip().split())
        if not cleaned:
            return ParsedPurchase("", None, None, DEFAULT_STATUS, DEFAULT_PRIORITY, "", text)

        note = ""
        note_match = cls.NOTE_REGEX.search(cleaned)
        if note_match:
            note = note_match.group(1).strip()
            cleaned = cleaned[: note_match.start()].strip()

        price, cleaned = cls._extract_price(cleaned)
        words = cleaned.split()

        status = DEFAULT_STATUS
        priority = DEFAULT_PRIORITY
        category = None
        content_words: list[str] = []

        for word in words:
            token = word.lower().strip(".,;:!?")
            if token in cls.STATUS_KEYWORDS:
                status = cls.STATUS_KEYWORDS[token]
                continue
            if token in cls.PRIORITY_KEYWORDS:
                priority = cls.PRIORITY_KEYWORDS[token]
                continue
            content_words.append(word)

        category_idx = None
        for idx, word in enumerate(content_words):
            matched_category = cls.detect_category(word)
            if matched_category and len(content_words) > 1:
                category = matched_category
                category_idx = idx

        if category_idx is None:
            for word in content_words:
                matched_category = cls.detect_category(word)
                if matched_category:
                    category = matched_category
                    break

        name_words = [word for idx, word in enumerate(content_words) if idx != category_idx]
        name = " ".join(name_words).strip(" -.,")
        return ParsedPurchase(
            name=name,
            price=price,
            category=category,
            status=status,
            priority=priority,
            note=note,
            raw_text=text,
        )

    @classmethod
    def detect_category(cls, text: str) -> str | None:
        value = text.lower().strip(".,;:!?")
        if not value:
            return None
        for canonical, aliases in CATEGORIES.items():
            if value == canonical.lower() or value in aliases:
                return canonical
        normalized = normalize_category(value)
        return None if normalized == DEFAULT_CATEGORY and value not in CATEGORIES[DEFAULT_CATEGORY] else normalized

    @classmethod
    def _extract_price(cls, text: str) -> tuple[int | None, str]:
        matches = list(cls.PRICE_REGEX.finditer(text))
        if not matches:
            return None, text
        match = matches[-1]
        raw_price = match.group(1).replace(" ", "").replace("\u00A0", "")
        try:
            price = int(raw_price)
        except ValueError:
            return None, text
        without_price = f"{text[:match.start()]} {text[match.end():]}".strip()
        return price, without_price
