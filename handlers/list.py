import os
from collections import defaultdict
from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile, Message

from services.db import list_purchases, get_total, get_stats, get_summary

CATEGORY_ICONS = {
    'Одежда': '👕',
    'Техника': '📱',
    'Еда': '🍔',
    'Поездки': '✈️',
    'Развлечения': '🎮',
    'Быт': '🏠',
    'Другое': '📌',
}


def format_purchase_groups(purchases: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in purchases:
        grouped[item['category']].append(item)

    lines = ['📋 Твои покупки']
    grand_total = 0
    for category in sorted(grouped.keys()):
        items = grouped[category]
        icon = CATEGORY_ICONS.get(category, '📌')
        lines.append(f'\n{icon} {category}')
        cat_total = 0
        for idx, item in enumerate(items, 1):
            lines.append(f'  {idx}. {item["name"]} — {item["price"]} ₽')
            cat_total += item['price']
        lines.append(f'  Σ {cat_total} ₽')
        grand_total += cat_total

    lines.append(f'\n━━━━━━━━━━━━━━')
    lines.append(f'💰 Итого: {grand_total} ₽')
    return '\n'.join(lines)


async def send_list(message: Message, category: str | None) -> None:
    purchases = list_purchases(message.from_user.id, category)
    if not purchases:
        await message.answer('📋 Нет покупок 📭')
        return

    await message.answer(format_purchase_groups(purchases))


async def cmd_list(message: Message) -> None:
    args = message.text.split()[1:]
    category = ' '.join(args) if args else None
    await send_list(message, category)


async def cmd_total(message: Message) -> None:
    args = message.text.split()[1:]
    category = ' '.join(args) if args else None
    if category:
        total = get_total(message.from_user.id, category)
        await message.answer(f'💰 {category}: {total} ₽')
        return

    total = get_total(message.from_user.id)
    await message.answer(f'💰 Всего потрачено: {total} ₽')


async def cmd_stats(message: Message) -> None:
    stats = get_stats(message.from_user.id)
    summary = get_summary(message.from_user.id)
    if not stats or summary['count'] == 0:
        await message.answer('📊 Нет данных. Добавь первую покупку!')
        return

    lines = ['📊 Статистика расходов']
    for item in stats:
        icon = CATEGORY_ICONS.get(item["category"], '📌')
        count_text = f'{item["count"]} покупок' if item["count"] > 1 else 'покупка'
        lines.append(f'{icon} {item["category"]}: {count_text} — {item["total"]} ₽')

    average = summary['total'] // summary['count'] if summary['count'] else 0
    lines.append('━━━━━━━━━━━━━━')
    lines.append(f'📦 Всего: {summary["count"]} покупок')
    lines.append(f'💰 Сумма: {summary["total"]} ₽')
    lines.append(f'📈 Среднее: {average} ₽/шт')
    await message.answer('\n'.join(lines))


async def cmd_export(message: Message) -> None:
    await export_purchases(message)


async def export_purchases(message: Message) -> None:
    purchases = list_purchases(message.from_user.id)
    if not purchases:
        await message.answer('❌ Нет покупок для экспорта')
        return

    file_path = os.path.join(os.getcwd(), f'expenses_{message.from_user.id}.txt')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('SpendNote — Экспорт покупок\n')
            f.write('=' * 50 + '\n\n')
            grouped = defaultdict(list)
            for item in purchases:
                grouped[item['category']].append(item)
            
            total_sum = 0
            for category in sorted(grouped.keys()):
                items = grouped[category]
                f.write(f'{category}\n')
                cat_sum = 0
                for item in items:
                    f.write(f'  • {item["name"]}: {item["price"]} ₽\n')
                    cat_sum += item['price']
                f.write(f'  Итого: {cat_sum} ₽\n\n')
                total_sum += cat_sum
            
            f.write(f'Всего расходов: {total_sum} ₽\n')
        
        await message.answer_document(FSInputFile(file_path), caption='📋 Экспорт покупок')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


def register_list_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_list, Command(commands=['list']))
    dp.message.register(cmd_total, Command(commands=['total']))
    dp.message.register(cmd_stats, Command(commands=['stats']))
    dp.message.register(cmd_export, Command(commands=['export']))
