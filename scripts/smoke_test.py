from __future__ import annotations

import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services import db
from services.parser import PurchaseParser


def main() -> None:
    original_path = db.DB_PATH
    try:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            db.DB_PATH = Path(tmp) / "test.db"
            db.init_db()

            parsed = PurchaseParser.parse("хочу ноутбук 80000 техника важно заметка: дождаться скидки")
            assert parsed.name == "ноутбук"
            assert parsed.price == 80000
            assert parsed.category == "Техника"
            assert parsed.priority == "high"

            user_id = 1001
            item_id = db.add_purchase(
                db.ItemInput(
                    user_id=user_id,
                    name=parsed.name,
                    price=parsed.price or 0,
                    category=parsed.category or db.DEFAULT_CATEGORY,
                    priority=parsed.priority,
                    note=parsed.note,
                )
            )
            assert db.get_purchase(user_id, item_id)["status"] == "planned"
            assert db.update_status(user_id, item_id, "bought")
            assert db.get_totals(user_id)["bought"]["total"] == 80000
    finally:
        db.DB_PATH = original_path
    print("smoke test ok")


if __name__ == "__main__":
    main()
