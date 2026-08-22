"""Tests for finance catalog export/upsert (no Qt required)."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from harrix_swiss_knife.apps.finance.catalog_sync import (
    export_finance_catalog,
    upsert_finance_catalog,
)

_SCHEMA_ONLY_SQL = """
CREATE TABLE currencies (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    subdivision INTEGER NOT NULL DEFAULT 100,
    ticker TEXT
);
CREATE TABLE categories (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type INTEGER NOT NULL,
    icon TEXT,
    name_local TEXT
);
CREATE TABLE standard_items (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    name_en TEXT,
    _id_categories INTEGER NOT NULL,
    FOREIGN KEY(_id_categories) REFERENCES categories(_id)
);
CREATE TABLE accounts (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    balance INTEGER NOT NULL DEFAULT 0,
    _id_currencies INTEGER NOT NULL
);
CREATE TABLE transactions (
    _id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount INTEGER NOT NULL,
    description TEXT NOT NULL,
    _id_categories INTEGER NOT NULL,
    _id_currencies INTEGER NOT NULL,
    date TEXT NOT NULL
);
"""


def _create_schema_only_db(db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(_SCHEMA_ONLY_SQL)
        conn.commit()
    return db_path


def _seed_source_db(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(
            """
            INSERT INTO currencies (code, name, symbol, subdivision, ticker)
            VALUES ('USD', 'US Dollar', '$', 100, NULL)
            """
        )
        conn.execute("INSERT INTO categories (name, type, icon, name_local) VALUES ('Food', 0, '🍔', 'Еда')")
        category_id = int(conn.execute("SELECT _id FROM categories WHERE name = 'Food'").fetchone()[0])
        conn.execute(
            "INSERT INTO standard_items (name, name_en, _id_categories) VALUES ('Вода', 'Drinking water', ?)",
            (category_id,),
        )
        conn.execute(
            "INSERT INTO accounts (name, balance, _id_currencies) VALUES ('Cash', 10, 1)",
        )
        conn.execute(
            """
            INSERT INTO transactions (amount, description, _id_categories, _id_currencies, date)
            VALUES (100, 'Lunch', ?, 1, '2024-01-01')
            """,
            (category_id,),
        )
        conn.commit()


def test_export_omits_ids_and_history(tmp_path: Path) -> None:
    """Catalog export has currencies/categories/items only, without database IDs."""
    db_path = _create_schema_only_db(tmp_path / "finance.db")
    _seed_source_db(db_path)
    catalog = export_finance_catalog(db_path)
    assert catalog["version"] == 1
    assert catalog["currencies"] == [
        {"code": "USD", "name": "US Dollar", "symbol": "$", "subdivision": 100, "ticker": None},
    ]
    assert catalog["categories"] == [{"name": "Food", "type": 0, "icon": "🍔", "name_local": "Еда"}]
    assert catalog["standard_items"] == [
        {"name": "Вода", "name_en": "Drinking water", "category_name": "Food", "category_type": 0},
    ]
    assert "transactions" not in catalog
    assert "accounts" not in catalog
    assert "_id" not in catalog["currencies"][0]


def test_upsert_updates_existing_preserves_ids_and_history(tmp_path: Path) -> None:
    """Matching keys update fields; transactions/accounts and IDs stay intact."""
    db_path = _create_schema_only_db(tmp_path / "finance.db")
    _seed_source_db(db_path)
    with sqlite3.connect(str(db_path)) as conn:
        currency_id = int(conn.execute("SELECT _id FROM currencies WHERE code = 'USD'").fetchone()[0])
        category_id = int(conn.execute("SELECT _id FROM categories WHERE name = 'Food'").fetchone()[0])
        item_id = int(conn.execute("SELECT _id FROM standard_items WHERE name = 'Вода'").fetchone()[0])

    catalog = {
        "version": 1,
        "currencies": [
            {"code": "USD", "name": "Dollar", "symbol": "US$", "subdivision": 100, "ticker": "USDUSD=X"},
            {"code": "EUR", "name": "Euro", "symbol": "€", "subdivision": 100, "ticker": None},
        ],
        "categories": [
            {"name": "Food", "type": 0, "icon": "🥗", "name_local": "Продукты"},
            {"name": "Transport", "type": 0, "icon": "🚗", "name_local": "Транспорт"},
        ],
        "standard_items": [
            {"name": "Вода", "name_en": "Water", "category_name": "Food", "category_type": 0},
            {"name": "Метро", "name_en": "Metro", "category_name": "Transport", "category_type": 0},
        ],
    }
    stats = upsert_finance_catalog(db_path, catalog)
    assert stats.currencies_updated == 1
    assert stats.currencies_inserted == 1
    assert stats.categories_updated == 1
    assert stats.categories_inserted == 1
    assert stats.standard_items_updated == 1
    assert stats.standard_items_inserted == 1

    with sqlite3.connect(str(db_path)) as conn:
        usd = conn.execute("SELECT _id, name, symbol, ticker FROM currencies WHERE code = 'USD'").fetchone()
        assert usd is not None
        assert int(usd[0]) == currency_id
        assert usd[1] == "Dollar"
        assert usd[2] == "US$"
        assert usd[3] == "USDUSD=X"
        food = conn.execute("SELECT _id, icon, name_local FROM categories WHERE name = 'Food'").fetchone()
        assert food is not None
        assert int(food[0]) == category_id
        assert food[1] == "🥗"
        assert food[2] == "Продукты"
        water = conn.execute("SELECT _id, name_en FROM standard_items WHERE name = 'Вода'").fetchone()
        assert water is not None
        assert int(water[0]) == item_id
        assert water[1] == "Water"
        assert int(conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]) == 1
        assert int(conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]) == 1
        assert int(conn.execute("SELECT COUNT(*) FROM currencies").fetchone()[0]) == 2
