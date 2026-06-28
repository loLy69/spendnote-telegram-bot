import sqlite3
from pathlib import Path
from typing import List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / 'shopping_assistant.db'


def _normalize_category(category: Optional[str]) -> Optional[str]:
    if not category:
        return 'Другое'
    normalized = category.strip().lower()
    mapping = {
        'одежда': 'Одежда',
        'техника': 'Техника',
        'еда': 'Еда',
        'поездки': 'Поездки',
        'развлечения': 'Развлечения',
        'быт': 'Быт',
        'другое': 'Другое',
    }
    return mapping.get(normalized, 'Другое')


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        conn.commit()


def add_purchase(user_id: int, name: str, price: int, category: str) -> int:
    normalized_category = _normalize_category(category) or 'Другое'
    with get_connection() as conn:
        cursor = conn.execute(
            'INSERT INTO purchases (user_id, name, price, category) VALUES (?, ?, ?, ?)',
            (user_id, name, price, normalized_category),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_purchases(user_id: int, category: Optional[str] = None) -> List[dict]:
    with get_connection() as conn:
        if category:
            normalized_category = _normalize_category(category)
            rows = conn.execute(
                'SELECT * FROM purchases WHERE user_id = ? AND category = ? ORDER BY category, id DESC',
                (user_id, normalized_category),
            ).fetchall()
        else:
            rows = conn.execute(
                'SELECT * FROM purchases WHERE user_id = ? ORDER BY category, id DESC',
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]


def get_total(user_id: int, category: Optional[str] = None) -> int:
    with get_connection() as conn:
        if category:
            normalized_category = _normalize_category(category)
            row = conn.execute(
                'SELECT COALESCE(SUM(price), 0) AS total FROM purchases WHERE user_id = ? AND category = ? ',
                (user_id, normalized_category),
            ).fetchone()
        else:
            row = conn.execute(
                'SELECT COALESCE(SUM(price), 0) AS total FROM purchases WHERE user_id = ? ',
                (user_id,),
            ).fetchone()
        return int(row['total']) if row else 0


def delete_purchase(user_id: int, purchase_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            'DELETE FROM purchases WHERE id = ? AND user_id = ?',
            (purchase_id, user_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def clear_purchases(user_id: int) -> int:
    with get_connection() as conn:
        cursor = conn.execute('DELETE FROM purchases WHERE user_id = ?', (user_id,))
        conn.commit()
        return cursor.rowcount


def get_stats(user_id: int) -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT category, COUNT(*) AS count, SUM(price) AS total FROM purchases WHERE user_id = ? GROUP BY category ORDER BY total DESC',
            (user_id,),
        ).fetchall()
        return [
            {
                'category': row['category'],
                'count': int(row['count']),
                'total': int(row['total']),
            }
            for row in rows
        ]


def get_summary(user_id: int) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT COUNT(*) AS count, COALESCE(SUM(price), 0) AS total FROM purchases WHERE user_id = ?',
            (user_id,),
        ).fetchone()
        return {
            'count': int(row['count']),
            'total': int(row['total']),
        }
