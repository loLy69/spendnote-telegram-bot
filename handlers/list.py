from __future__ import annotations

import csv
import tempfile
from collections import defaultdict
from html import escape
from pathlib import Path

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from keyboards.categories import CATEGORY_ICONS, format_priority, get_item_actions
from keyboards.main import get_main_keyboard
from services.db import (
    STATUSES,
    get_budget,
    get_purchase,
    get_stats,
    get_totals,
    iter_export_rows,
    list_purchases,
    normalize_status,
    set_budget,
    update_status,
)
from services.fsm import SettingsStates


def money(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₽"


def format_items(items: list[dict], title: str) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item["category"]].append(item)

    lines = [f"<b>{title}</b>"]
    total = 0
    for category, category_items in grouped.items():
        lines.append(f"\n{CATEGORY_ICONS.get(category, '📌')} <b>{category}</b>")
        for item in category_items:
            total += int(item["price"])
            note = f"\n   📝 {escape(item['note'])}" if item.get("note") else ""
            lines.append(
                f"#{item['id']} {escape(item['name'])} - {money(int(item['price']))}\n"
                f"   {format_priority(item['priority'])}{note}"
            )
    lines.append(f"\n<b>Итого: {money(total)}</b>")
    return "\n".join(lines)


async def send_items(message: Message, status: str | None = "planned") -> None:
    items = list_purchases(message.from_user.id, status=status)
    if not items:
        label = STATUSES.get(status or "planned", "Список")
        await message.answer(f"{label}: пока пусто.", reply_markup=get_main_keyboard())
        return

    title = "📌 План покупок" if status == "planned" else "✅ Куплено" if status == "bought" else "📋 Покупки"
    await message.answer(format_items(items, title), reply_markup=get_main_keyboard(), parse_mode="HTML")

    for item in items[:5]:
        await message.answer(
            f"#{item['id']} {item['name']} - {money(int(item['price']))}",
            reply_markup=get_item_actions(item["id"], item["status"]),
        )


async def menu_planned(message: Message) -> None:
    await send_items(message, "planned")


async def menu_bought(message: Message) -> None:
    await send_items(message, "bought")


async def cmd_list(message: Message) -> None:
    args = message.text.split()[1:]
    status = None if args and args[0].lower() in {"all", "все"} else normalize_status(args[0]) if args else "planned"
    await send_items(message, status=status)


async def cmd_budget(message: Message, state: FSMContext) -> None:
    args = message.text.split()[1:]
    if args:
        try:
            amount = int(args[0].replace(" ", "").replace("\u00A0", ""))
        except ValueError:
            await message.answer("Бюджет нужно указать числом: /budget 60000")
            return
        set_budget(message.from_user.id, amount)
        await message.answer(f"💰 Бюджет установлен: <b>{money(amount)}</b>", parse_mode="HTML")
        return

    budget = get_budget(message.from_user.id)
    if budget:
        await message.answer(f"💰 Текущий бюджет: <b>{money(budget)}</b>\nЧтобы изменить: /budget 60000", parse_mode="HTML")
        return

    await state.set_state(SettingsStates.waiting_for_budget)
    await message.answer("💰 Напиши месячный бюджет числом, например: <b>60000</b>", parse_mode="HTML")


async def handle_budget_value(message: Message, state: FSMContext) -> None:
    try:
        amount = int((message.text or "").replace(" ", "").replace("\u00A0", ""))
    except ValueError:
        await message.answer("Не похоже на число. Например: <b>60000</b>", parse_mode="HTML")
        return
    set_budget(message.from_user.id, amount)
    await state.clear()
    await message.answer(f"Готово. Бюджет: <b>{money(amount)}</b>", reply_markup=get_main_keyboard(), parse_mode="HTML")


async def cmd_stats(message: Message) -> None:
    totals = get_totals(message.from_user.id)
    planned = totals["planned"]["total"]
    bought = totals["bought"]["total"]
    budget = int(totals["budget"])

    lines = ["📊 <b>Финансовая картина</b>\n"]
    lines.append(f"📌 В плане: {totals['planned']['count']} на <b>{money(planned)}</b>")
    lines.append(f"✅ Куплено: {totals['bought']['count']} на <b>{money(bought)}</b>")
    if totals["skipped"]["count"]:
        lines.append(f"🕒 Отложено: {totals['skipped']['count']} на <b>{money(totals['skipped']['total'])}</b>")

    if budget:
        remaining = budget - planned
        marker = "🟢" if remaining >= 0 else "🔴"
        lines.append(f"\n💰 Бюджет: <b>{money(budget)}</b>")
        lines.append(f"{marker} После плана: <b>{money(remaining)}</b>")
    else:
        lines.append("\n💰 Бюджет не задан. Команда: /budget 60000")

    stats = get_stats(message.from_user.id, status="planned")
    if stats:
        lines.append("\n<b>План по категориям:</b>")
        for item in stats:
            lines.append(f"{CATEGORY_ICONS.get(item['category'], '📌')} {item['category']}: {money(int(item['total']))}")

    await message.answer("\n".join(lines), reply_markup=get_main_keyboard(), parse_mode="HTML")


async def cmd_export(message: Message) -> None:
    rows = list(iter_export_rows(message.from_user.id))
    if not rows:
        await message.answer("Экспортировать пока нечего.")
        return

    with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", suffix=".csv", delete=False) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["id", "name", "price", "category", "status", "priority", "note", "created_at"],
        )
        writer.writeheader()
        writer.writerows(rows)
        file_path = file.name

    try:
        await message.answer_document(FSInputFile(file_path, filename="spendnote_export.csv"), caption="📤 Экспорт SpendNote")
    finally:
        Path(file_path).unlink(missing_ok=True)


async def cmd_buy(message: Message) -> None:
    args = message.text.split()[1:]
    if not args:
        await message.answer("Укажи ID: /buy 12")
        return
    try:
        item_id = int(args[0])
    except ValueError:
        await message.answer("ID должен быть числом.")
        return
    await _set_status(message, item_id, "bought")


async def cmd_skip(message: Message) -> None:
    args = message.text.split()[1:]
    if not args:
        await message.answer("Укажи ID: /skip 12")
        return
    try:
        item_id = int(args[0])
    except ValueError:
        await message.answer("ID должен быть числом.")
        return
    await _set_status(message, item_id, "skipped")


async def _set_status(message: Message, item_id: int, status: str) -> None:
    item = get_purchase(message.from_user.id, item_id)
    if not item:
        await message.answer("Не нашел такую покупку.")
        return
    update_status(message.from_user.id, item_id, status)
    label = STATUSES[status]
    await message.answer(f"{label}: #{item_id} {escape(item['name'])}", reply_markup=get_main_keyboard(), parse_mode="HTML")


async def handle_status_callback(callback: CallbackQuery) -> None:
    action, raw_id = callback.data.split(":", 1)
    item_id = int(raw_id)
    status = "bought" if action == "buy" else "skipped"
    updated = update_status(callback.from_user.id, item_id, status)
    if not updated:
        await callback.answer("Покупка не найдена", show_alert=True)
        return
    await callback.message.edit_text(f"{STATUSES[status]}: #{item_id}")
    await callback.answer("Готово")


def register_list_handlers(dp: Dispatcher) -> None:
    dp.message.register(cmd_list, Command(commands=["list"]))
    dp.message.register(menu_planned, F.text == "📌 План")
    dp.message.register(menu_bought, F.text == "✅ Куплено")
    dp.message.register(cmd_budget, Command(commands=["budget"]))
    dp.message.register(cmd_budget, F.text == "💰 Бюджет")
    dp.message.register(handle_budget_value, SettingsStates.waiting_for_budget)
    dp.message.register(cmd_stats, Command(commands=["stats"]))
    dp.message.register(cmd_stats, F.text == "📊 Статистика")
    dp.message.register(cmd_export, Command(commands=["export"]))
    dp.message.register(cmd_export, F.text == "📤 Экспорт")
    dp.message.register(cmd_buy, Command(commands=["buy"]))
    dp.message.register(cmd_skip, Command(commands=["skip"]))
    dp.callback_query.register(handle_status_callback, F.data.startswith("buy:") | F.data.startswith("skip:"))
