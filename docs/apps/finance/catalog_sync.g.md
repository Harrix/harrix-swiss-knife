---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `catalog_sync.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FinanceCatalogUpsertStats`](#%EF%B8%8F-class-financecatalogupsertstats)
- [🔧 Function `create_empty_finance_database`](#-function-create_empty_finance_database)
- [🔧 Function `export_finance_catalog`](#-function-export_finance_catalog)
- [🔧 Function `load_finance_catalog_json`](#-function-load_finance_catalog_json)
- [🔧 Function `normalize_finance_catalog`](#-function-normalize_finance_catalog)
- [🔧 Function `upsert_finance_catalog`](#-function-upsert_finance_catalog)

</details>

## 🏛️ Class `FinanceCatalogUpsertStats`

```python
class FinanceCatalogUpsertStats
```

Counts from a finance catalog upsert into a target database.

<details>
<summary>Code:</summary>

```python
class FinanceCatalogUpsertStats:

    currencies_inserted: int = 0
    currencies_updated: int = 0
    categories_inserted: int = 0
    categories_updated: int = 0
    standard_items_inserted: int = 0
    standard_items_updated: int = 0
```

</details>

## 🔧 Function `create_empty_finance_database`

```python
def create_empty_finance_database(db_path: Path, recover_sql_path: Path) -> None
```

Create a new SQLite file by executing `recover.sql` (schema plus base seed).

<details>
<summary>Code:</summary>

```python
def create_empty_finance_database(db_path: Path, recover_sql_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    sql = recover_sql_path.read_text(encoding="utf-8")
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(sql)
        conn.commit()
```

</details>

## 🔧 Function `export_finance_catalog`

```python
def export_finance_catalog(db_path: Path) -> dict[str, Any]
```

Read catalog tables from `db_path` into a JSON-serializable object.

Returns:

- `dict[str, Any]`: Object with `version`, `currencies`, `categories`, and
  `standard_items`. Database `_id` values are omitted; standard items store
  category `name` and `type` instead of a foreign key.

<details>
<summary>Code:</summary>

```python
def export_finance_catalog(db_path: Path) -> dict[str, Any]:
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
```

</details>

## 🔧 Function `load_finance_catalog_json`

```python
def load_finance_catalog_json(path: Path) -> dict[str, Any]
```

Load and lightly validate a finance catalog JSON file.

<details>
<summary>Code:</summary>

```python
def load_finance_catalog_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return normalize_finance_catalog(raw)
```

</details>

## 🔧 Function `normalize_finance_catalog`

```python
def normalize_finance_catalog(raw: Any) -> dict[str, Any]
```

Validate catalog shape and return a normalized dict.

<details>
<summary>Code:</summary>

```python
def normalize_finance_catalog(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        msg = "finance_catalog.json root must be an object"
        raise TypeError(msg)
    return {
        "version": int(raw.get("version") or 1),
        "currencies": _normalize_currencies(raw.get("currencies")),
        "categories": _normalize_categories(raw.get("categories")),
        "standard_items": _normalize_standard_items(raw.get("standard_items")),
    }
```

</details>

## 🔧 Function `upsert_finance_catalog`

```python
def upsert_finance_catalog(db_path: Path, catalog: dict[str, Any]) -> FinanceCatalogUpsertStats
```

Insert or update catalog rows; never touch accounts or transactions.

Existing local-only rows are left unchanged. Existing `_id` values are
preserved so transactions and standard-item foreign keys stay linked.

<details>
<summary>Code:</summary>

```python
def upsert_finance_catalog(db_path: Path, catalog: dict[str, Any]) -> FinanceCatalogUpsertStats:
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
```

</details>
