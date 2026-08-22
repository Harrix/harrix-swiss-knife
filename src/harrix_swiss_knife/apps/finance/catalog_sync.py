"""Export and upsert finance catalog tables without touching money history.

Uses stdlib `sqlite3` so pack/install and unit tests do not need Qt SQL.
Keys are currency `code`, category `(name, type)`, and standard item `name`.
Tables `accounts`, `transactions`, `exchange_rates`, `currency_exchanges`, and
`settings` are never read or written.

"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True)
class FinanceCatalogUpsertStats:
    """Counts from a finance catalog upsert into a target database."""

    currencies_inserted: int = 0
    currencies_updated: int = 0
    categories_inserted: int = 0
    categories_updated: int = 0
    standard_items_inserted: int = 0
    standard_items_updated: int = 0


def create_empty_finance_database(db_path: Path, recover_sql_path: Path) -> None:
    """Create a new SQLite file by executing `recover.sql` (schema plus base seed)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = recover_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(sql)
        conn.commit()


def export_finance_catalog(db_path: Path) -> dict[str, Any]:
    """Read catalog tables from `db_path` into a JSON-serializable object.

    Returns:

    - `dict[str, Any]`: Object with `version`, `currencies`, `categories`, and
      `standard_items`. Database `_id` values are omitted; standard items store
      category `name` and `type` instead of a foreign key.

    """
    if not db_path.is_file():
        msg = f"Finance database not found: {db_path}"
        raise FileNotFoundError(msg)

    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        currency_rows = conn.execute(
            """
            SELECT code, name, symbol, subdivision, ticker
            FROM currencies
            ORDER BY code COLLATE NOCASE
            """
        ).fetchall()
        category_rows = conn.execute(
            """
            SELECT name, type, IFNULL(icon, '') AS icon, IFNULL(name_local, '') AS name_local
            FROM categories
            ORDER BY type, name COLLATE NOCASE
            """
        ).fetchall()
        item_rows = conn.execute(
            """
            SELECT
                standard_items.name AS name,
                IFNULL(standard_items.name_en, '') AS name_en,
                categories.name AS category_name,
                categories.type AS category_type
            FROM standard_items
            JOIN categories ON categories._id = standard_items._id_categories
            ORDER BY standard_items.name COLLATE NOCASE
            """
        ).fetchall()

    return {
        "version": 1,
        "currencies": [
            {
                "code": str(row["code"]),
                "name": str(row["name"]),
                "symbol": str(row["symbol"]),
                "subdivision": int(row["subdivision"]),
                "ticker": str(row["ticker"]) if row["ticker"] is not None else None,
            }
            for row in currency_rows
        ],
        "categories": [
            {
                "name": str(row["name"]),
                "type": int(row["type"]),
                "icon": str(row["icon"] or ""),
                "name_local": str(row["name_local"] or ""),
            }
            for row in category_rows
        ],
        "standard_items": [
            {
                "name": str(row["name"]),
                "name_en": str(row["name_en"] or ""),
                "category_name": str(row["category_name"]),
                "category_type": int(row["category_type"]),
            }
            for row in item_rows
        ],
    }


def load_finance_catalog_json(path: Path) -> dict[str, Any]:
    """Load and lightly validate a finance catalog JSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return normalize_finance_catalog(raw)


def normalize_finance_catalog(raw: Any) -> dict[str, Any]:
    """Validate catalog shape and return a normalized dict."""
    if not isinstance(raw, dict):
        msg = "finance_catalog.json root must be an object"
        raise TypeError(msg)
    return {
        "version": int(raw.get("version") or 1),
        "currencies": _normalize_currencies(raw.get("currencies")),
        "categories": _normalize_categories(raw.get("categories")),
        "standard_items": _normalize_standard_items(raw.get("standard_items")),
    }


def upsert_finance_catalog(db_path: Path, catalog: dict[str, Any]) -> FinanceCatalogUpsertStats:
    """Insert or update catalog rows; never touch accounts or transactions.

    Existing local-only rows are left unchanged. Existing `_id` values are
    preserved so transactions and standard-item foreign keys stay linked.

    """
    normalized = normalize_finance_catalog(catalog)
    if not db_path.is_file():
        msg = f"Finance database not found: {db_path}"
        raise FileNotFoundError(msg)

    currencies_inserted = 0
    currencies_updated = 0
    categories_inserted = 0
    categories_updated = 0
    standard_items_inserted = 0
    standard_items_updated = 0

    with sqlite3.connect(str(db_path)) as conn:
        for currency in normalized["currencies"]:
            row = conn.execute("SELECT _id FROM currencies WHERE code = ?", (currency["code"],)).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO currencies (code, name, symbol, subdivision, ticker)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        currency["code"],
                        currency["name"],
                        currency["symbol"],
                        currency["subdivision"],
                        currency["ticker"],
                    ),
                )
                currencies_inserted += 1
            else:
                conn.execute(
                    """
                    UPDATE currencies
                    SET name = ?, symbol = ?, subdivision = ?, ticker = ?
                    WHERE _id = ?
                    """,
                    (
                        currency["name"],
                        currency["symbol"],
                        currency["subdivision"],
                        currency["ticker"],
                        int(row[0]),
                    ),
                )
                currencies_updated += 1

        for category in normalized["categories"]:
            row = conn.execute(
                "SELECT _id FROM categories WHERE name = ? AND type = ?",
                (category["name"], category["type"]),
            ).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO categories (name, type, icon, name_local)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        category["name"],
                        category["type"],
                        category["icon"] or None,
                        category["name_local"] or None,
                    ),
                )
                categories_inserted += 1
            else:
                conn.execute(
                    """
                    UPDATE categories
                    SET icon = ?, name_local = ?
                    WHERE _id = ?
                    """,
                    (
                        category["icon"] or None,
                        category["name_local"] or None,
                        int(row[0]),
                    ),
                )
                categories_updated += 1

        for item in normalized["standard_items"]:
            category_row = conn.execute(
                "SELECT _id FROM categories WHERE name = ? AND type = ?",
                (item["category_name"], item["category_type"]),
            ).fetchone()
            if category_row is None:
                msg = (
                    f"standard_items {item['name']!r} references missing category "
                    f"{item['category_name']!r} type {item['category_type']}"
                )
                raise ValueError(msg)
            category_id = int(category_row[0])
            row = conn.execute("SELECT _id FROM standard_items WHERE name = ?", (item["name"],)).fetchone()
            if row is None:
                conn.execute(
                    """
                    INSERT INTO standard_items (name, name_en, _id_categories)
                    VALUES (?, ?, ?)
                    """,
                    (item["name"], item["name_en"] or None, category_id),
                )
                standard_items_inserted += 1
            else:
                conn.execute(
                    """
                    UPDATE standard_items
                    SET name_en = ?, _id_categories = ?
                    WHERE _id = ?
                    """,
                    (item["name_en"] or None, category_id, int(row[0])),
                )
                standard_items_updated += 1
        conn.commit()

    return FinanceCatalogUpsertStats(
        currencies_inserted=currencies_inserted,
        currencies_updated=currencies_updated,
        categories_inserted=categories_inserted,
        categories_updated=categories_updated,
        standard_items_inserted=standard_items_inserted,
        standard_items_updated=standard_items_updated,
    )


def _normalize_categories(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        msg = "finance_catalog.json must contain a 'categories' list"
        raise TypeError(msg)
    categories: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            msg = f"categories[{index}] must be an object"
            raise TypeError(msg)
        name = str(item.get("name") or "").strip()
        if not name:
            msg = f"categories[{index}] is missing non-empty 'name'"
            raise ValueError(msg)
        categories.append(
            {
                "name": name,
                "type": int(item.get("type") or 0),
                "icon": str(item.get("icon") or ""),
                "name_local": str(item.get("name_local") or ""),
            }
        )
    return categories


def _normalize_currencies(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        msg = "finance_catalog.json must contain a 'currencies' list"
        raise TypeError(msg)
    currencies: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            msg = f"currencies[{index}] must be an object"
            raise TypeError(msg)
        code = str(item.get("code") or "").strip()
        name = str(item.get("name") or "").strip()
        symbol = str(item.get("symbol") or "").strip()
        if not code:
            msg = f"currencies[{index}] is missing non-empty 'code'"
            raise ValueError(msg)
        if not name:
            msg = f"currencies[{index}] is missing non-empty 'name'"
            raise ValueError(msg)
        if not symbol:
            msg = f"currencies[{index}] is missing non-empty 'symbol'"
            raise ValueError(msg)
        ticker_raw = item.get("ticker")
        ticker = str(ticker_raw).strip() if ticker_raw not in (None, "") else None
        currencies.append(
            {
                "code": code,
                "name": name,
                "symbol": symbol,
                "subdivision": int(item.get("subdivision") if item.get("subdivision") is not None else 100),
                "ticker": ticker,
            }
        )
    return currencies


def _normalize_standard_items(raw: Any) -> list[dict[str, Any]]:
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        msg = "finance_catalog.json must contain a 'standard_items' list"
        raise TypeError(msg)
    items: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            msg = f"standard_items[{index}] must be an object"
            raise TypeError(msg)
        name = str(item.get("name") or "").strip()
        category_name = str(item.get("category_name") or "").strip()
        if not name:
            msg = f"standard_items[{index}] is missing non-empty 'name'"
            raise ValueError(msg)
        if not category_name:
            msg = f"standard_items[{index}] is missing non-empty 'category_name'"
            raise ValueError(msg)
        items.append(
            {
                "name": name,
                "name_en": str(item.get("name_en") or ""),
                "category_name": category_name,
                "category_type": int(item.get("category_type") or 0),
            }
        )
    return items
