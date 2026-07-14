from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).resolve().parent.parent / "shopping_assistant.db"

DEFAULT_CATEGORY = "Другое"
DEFAULT_STATUS = "planned"
DEFAULT_PRIORITY = "normal"

CATEGORIES = {
    "Еда": ["еда", "еды", "еду", "продукты", "кофе", "кафе", "ресторан", "обед", "ужин"],
    "Техника": ["техника", "технику", "телефон", "айфон", "ноутбук", "планшет", "гаджет", "наушники"],
    "Одежда": ["одежда", "одежду", "кроссовки", "футболка", "куртка", "джинсы", "обувь"],
    "Дом": ["дом", "быт", "бытовая", "уборка", "мыло", "шампунь", "посуда", "мебель"],
    "Транспорт": ["транспорт", "такси", "метро", "бензин", "поездка", "билет", "самолет"],
    "Здоровье": ["здоровье", "аптека", "лекарства", "врач", "стоматолог", "витамины"],
    "Развлечения": ["кино", "игра", "игры", "концерт", "развлечения", "хобби", "подписка"],
    "Подарки": ["подарок", "подарки", "цветы", "сюрприз"],
    "Другое": ["другое", "прочее", "разное"],
}

STATUSES = {
    "planned": "В плане",
    "bought": "Куплено",
    "skipped": "Отложено",
}

PRIORITIES = {
    "low": "Можно позже",
    "normal": "Обычный",
    "high": "Важно",
}


@dataclass(frozen=True)
class ItemInput:
    user_id: int
    name: str
    price: int
    category: str = DEFAULT_CATEGORY
    status: str = DEFAULT_STATUS
    priority: str = DEFAULT_PRIORITY
    note: str = ""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def normalize_category(category: str | None) -> str:
    if not category:
        return DEFAULT_CATEGORY
    value = category.strip().lower()
    for canonical, aliases in CATEGORIES.items():
        if value == canonical.lower() or value in aliases:
            return canonical
    return DEFAULT_CATEGORY


def normalize_status(status: str | None) -> str:
    if not status:
        return DEFAULT_STATUS
    value = status.strip().lower()
    aliases = {
        "planned": "planned",
        "plan": "planned",
        "хочу": "planned",
        "план": "planned",
        "купить": "planned",
        "bought": "bought",
        "buy": "bought",
        "done": "bought",
        "куплено": "bought",
        "купил": "bought",
        "купила": "bought",
        "skipped": "skipped",
        "skip": "skipped",
        "потом": "skipped",
        "отложено": "skipped",
    }
    return aliases.get(value, DEFAULT_STATUS)


def normalize_priority(priority: str | None) -> str:
    if not priority:
        return DEFAULT_PRIORITY
    value = priority.strip().lower()
    aliases = {
        "low": "low",
        "низкий": "low",
        "потом": "low",
        "normal": "normal",
        "средний": "normal",
        "обычный": "normal",
        "high": "high",
        "важно": "high",
        "срочно": "high",
        "must": "high",
    }
    return aliases.get(value, DEFAULT_PRIORITY)


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                monthly_budget INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL CHECK(price >= 0),
                category TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'planned',
                priority TEXT NOT NULL DEFAULT 'normal',
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        _migrate_purchases(conn)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_purchases_user_status ON purchases(user_id, status, created_at DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_purchases_user_category ON purchases(user_id, category)"
        )
        conn.commit()


def _migrate_purchases(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "purchases"):
        return

    columns = _column_names(conn, "purchases")
    required = {"id", "user_id", "name", "price", "category", "status", "priority", "note", "created_at", "updated_at"}
    if required.issubset(columns):
        return

    conn.execute("ALTER TABLE purchases RENAME TO purchases_legacy")
    conn.execute(
        """
        CREATE TABLE purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price INTEGER NOT NULL CHECK(price >= 0),
            category TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'planned',
            priority TEXT NOT NULL DEFAULT 'normal',
            note TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    legacy_columns = _column_names(conn, "purchases_legacy")
    created_expr = "COALESCE(created_at, ?)" if "created_at" in legacy_columns else "?"
    conn.execute(
        f"""
        INSERT INTO purchases (id, user_id, name, price, category, status, priority, note, created_at, updated_at)
        SELECT id, user_id, name, price, category, 'planned', 'normal', '', {created_expr}, ?
        FROM purchases_legacy
        """,
        (now_iso(), now_iso()),
    )
    conn.execute("DROP TABLE purchases_legacy")


def upsert_user(user_id: int, username: str | None, full_name: str | None) -> None:
    timestamp = now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username, full_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                updated_at = excluded.updated_at
            """,
            (user_id, username or "", full_name or "", timestamp, timestamp),
        )
        conn.commit()


def add_purchase(item: ItemInput) -> int:
    timestamp = now_iso()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO purchases (user_id, name, price, category, status, priority, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.user_id,
                item.name.strip(),
                int(item.price),
                normalize_category(item.category),
                normalize_status(item.status),
                normalize_priority(item.priority),
                item.note.strip(),
                timestamp,
                timestamp,
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_purchases(user_id: int, status: str | None = None, category: str | None = None, limit: int = 50) -> list[dict]:
    where = ["user_id = ?"]
    params: list[object] = [user_id]
    if status:
        where.append("status = ?")
        params.append(normalize_status(status))
    if category:
        where.append("category = ?")
        params.append(normalize_category(category))
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT * FROM purchases
            WHERE {" AND ".join(where)}
            ORDER BY
                CASE priority WHEN 'high' THEN 0 WHEN 'normal' THEN 1 ELSE 2 END,
                id DESC
            LIMIT ?
            """,
            params,
        ).fetchall()
        return [dict(row) for row in rows]


def get_purchase(user_id: int, purchase_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM purchases WHERE user_id = ? AND id = ?",
            (user_id, purchase_id),
        ).fetchone()
        return dict(row) if row else None


def update_status(user_id: int, purchase_id: int, status: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE purchases SET status = ?, updated_at = ? WHERE user_id = ? AND id = ?",
            (normalize_status(status), now_iso(), user_id, purchase_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_purchase(user_id: int, purchase_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM purchases WHERE id = ? AND user_id = ?",
            (purchase_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_purchases(user_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM purchases WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount


def set_budget(user_id: int, amount: int) -> None:
    timestamp = now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, monthly_budget, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET monthly_budget = excluded.monthly_budget, updated_at = excluded.updated_at
            """,
            (user_id, max(0, int(amount)), timestamp, timestamp),
        )
        conn.commit()


def get_budget(user_id: int) -> int:
    with get_connection() as conn:
        row = conn.execute("SELECT monthly_budget FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return int(row["monthly_budget"]) if row else 0


def get_totals(user_id: int) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT status, COUNT(*) AS count, COALESCE(SUM(price), 0) AS total
            FROM purchases
            WHERE user_id = ?
            GROUP BY status
            """,
            (user_id,),
        ).fetchall()
        result = {status: {"count": 0, "total": 0} for status in STATUSES}
        for row in rows:
            result[row["status"]] = {"count": int(row["count"]), "total": int(row["total"])}
        result["budget"] = get_budget(user_id)
        return result


def get_stats(user_id: int, status: str | None = None) -> list[dict]:
    where = ["user_id = ?"]
    params: list[object] = [user_id]
    if status:
        where.append("status = ?")
        params.append(normalize_status(status))

    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT category, COUNT(*) AS count, COALESCE(SUM(price), 0) AS total
            FROM purchases
            WHERE {" AND ".join(where)}
            GROUP BY category
            ORDER BY total DESC
            """,
            params,
        ).fetchall()
        return [dict(row) for row in rows]


def iter_export_rows(user_id: int) -> Iterable[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, price, category, status, priority, note, created_at
            FROM purchases
            WHERE user_id = ?
            ORDER BY status, category, id DESC
            """,
            (user_id,),
        ).fetchall()
        for row in rows:
            yield dict(row)
