---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_log_transfer.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FoodLogTransferItem`](#%EF%B8%8F-class-foodlogtransferitem)
- [🏛️ Class `FoodLogTransferPayload`](#%EF%B8%8F-class-foodlogtransferpayload)
- [🔧 Function `build_transfer_item_from_log_row`](#-function-build_transfer_item_from_log_row)
- [🔧 Function `group_items_by_date`](#-function-group_items_by_date)
- [🔧 Function `is_food_log_transfer_path`](#-function-is_food_log_transfer_path)
- [🔧 Function `item_to_json`](#-function-item_to_json)
- [🔧 Function `items_to_tsv`](#-function-items_to_tsv)
- [🔧 Function `name_en_lookup`](#-function-name_en_lookup)
- [🔧 Function `parse_transfer_file`](#-function-parse_transfer_file)
- [🔧 Function `parse_transfer_payload`](#-function-parse_transfer_payload)
- [🔧 Function `payload_dict`](#-function-payload_dict)
- [🔧 Function `transfer_filename_for_date`](#-function-transfer_filename_for_date)
- [🔧 Function `transfer_items_to_parsed`](#-function-transfer_items_to_parsed)
- [🔧 Function `write_transfer_files`](#-function-write_transfer_files)

</details>

## 🏛️ Class `FoodLogTransferItem`

```python
class FoodLogTransferItem
```

One food log row ready for JSON transfer or dialog preview.

<details>
<summary>Code:</summary>

```python
class FoodLogTransferItem:

    name: str
    weight: float
    is_drink: bool
    calories_per_100g: float | None
    date: str
    name_en: str | None = None
```

</details>

## 🏛️ Class `FoodLogTransferPayload`

```python
class FoodLogTransferPayload
```

Parsed transfer file contents.

<details>
<summary>Code:</summary>

```python
class FoodLogTransferPayload:

    default_date: str
    items: list[FoodLogTransferItem]
    exported_at: str | None = None
```

</details>

## 🔧 Function `build_transfer_item_from_log_row`

```python
def build_transfer_item_from_log_row(*, date: str, name: str, name_en: str | None, weight: float | None, calories_per_100g: float | None, is_drink: bool) -> FoodLogTransferItem | None
```

Build a transfer item from a food_log DB row, or `None` when incomplete.

<details>
<summary>Code:</summary>

```python
def build_transfer_item_from_log_row(
    *,
    date: str,
    name: str,
    name_en: str | None,
    weight: float | None,
    calories_per_100g: float | None,
    is_drink: bool,
) -> FoodLogTransferItem | None:
    day = (date or "").strip()[:10]
    food_name = (name or "").strip()
    if not day or not _DATE_RE.match(day) or not food_name:
        return None
    if weight is None or weight <= 0:
        return None
    if calories_per_100g is None or calories_per_100g < 0:
        return None
    return FoodLogTransferItem(
        name=food_name,
        name_en=_optional_name(name_en),
        weight=float(weight),
        is_drink=bool(is_drink),
        calories_per_100g=float(calories_per_100g),
        date=day,
    )
```

</details>

## 🔧 Function `group_items_by_date`

```python
def group_items_by_date(items: list[FoodLogTransferItem]) -> dict[str, list[FoodLogTransferItem]]
```

Group transfer items by `date` (sorted keys when iterated via `sorted`).

<details>
<summary>Code:</summary>

```python
def group_items_by_date(items: list[FoodLogTransferItem]) -> dict[str, list[FoodLogTransferItem]]:
    grouped: dict[str, list[FoodLogTransferItem]] = {}
    for item in items:
        grouped.setdefault(item.date, []).append(item)
    return grouped
```

</details>

## 🔧 Function `is_food_log_transfer_path`

```python
def is_food_log_transfer_path(file_path: str | Path) -> bool
```

Return `True` when path looks like a transfer JSON file by suffix.

<details>
<summary>Code:</summary>

```python
def is_food_log_transfer_path(file_path: str | Path) -> bool:
    return Path(file_path).suffix.lower() == ".json"
```

</details>

## 🔧 Function `item_to_json`

```python
def item_to_json(item: FoodLogTransferItem) -> dict[str, Any]
```

Serialize one transfer item (always weight / kcal per 100 g).

<details>
<summary>Code:</summary>

```python
def item_to_json(item: FoodLogTransferItem) -> dict[str, Any]:
    return {
        "name": item.name,
        "name_en": item.name_en,
        "is_drink": item.is_drink,
        "weight": item.weight,
        "calorie_mode": "weight",
        "calories_per_100g": item.calories_per_100g,
        "portion_calories": None,
        "date": item.date,
    }
```

</details>

## 🔧 Function `items_to_tsv`

```python
def items_to_tsv(items: list[FoodLogTransferItem]) -> str
```

Convert transfer items to FoodTableDialog TSV (Name/Weight/Calories/Mode/Drink).

<details>
<summary>Code:</summary>

```python
def items_to_tsv(items: list[FoodLogTransferItem]) -> str:
    lines: list[str] = []
    for item in items:
        calories = item.calories_per_100g or 0
        drink = "yes" if item.is_drink else "no"
        lines.append(f"{item.name}\t{item.weight:g}\t{calories:g}\tweight\t{drink}")
    return "\n".join(lines)
```

</details>

## 🔧 Function `name_en_lookup`

```python
def name_en_lookup(items: list[FoodLogTransferItem]) -> dict[str, str]
```

Map casefolded name → English name from transfer items.

<details>
<summary>Code:</summary>

```python
def name_en_lookup(items: list[FoodLogTransferItem]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        if item.name_en:
            result[item.name.casefold()] = item.name_en
    return result
```

</details>

## 🔧 Function `parse_transfer_file`

```python
def parse_transfer_file(path: Path) -> FoodLogTransferPayload
```

Load and validate a transfer JSON file.

<details>
<summary>Code:</summary>

```python
def parse_transfer_file(path: Path) -> FoodLogTransferPayload:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return parse_transfer_payload(raw)
```

</details>

## 🔧 Function `parse_transfer_payload`

```python
def parse_transfer_payload(raw: Any) -> FoodLogTransferPayload
```

Validate a transfer JSON object.

<details>
<summary>Code:</summary>

```python
def parse_transfer_payload(raw: Any) -> FoodLogTransferPayload:
    if not isinstance(raw, dict):
        msg = "Food log transfer root must be an object"
        raise TypeError(msg)
    if raw.get("format") != FORMAT_ID:
        msg = f"Unsupported format id (expected {FORMAT_ID!r})"
        raise ValueError(msg)
    version = raw.get("version", FORMAT_VERSION)
    if not isinstance(version, int) or version < 1 or version > FORMAT_VERSION:
        msg = f"Unsupported format version: {version!r}"
        raise ValueError(msg)
    default_date = str(raw.get("default_date") or "").strip()[:10]
    if not default_date or not _DATE_RE.match(default_date):
        msg = "default_date must be YYYY-MM-DD"
        raise ValueError(msg)
    items_raw = raw.get("items")
    if not isinstance(items_raw, list) or not items_raw:
        msg = "items must be a non-empty list"
        raise ValueError(msg)
    items: list[FoodLogTransferItem] = []
    for index, entry in enumerate(items_raw):
        try:
            items.append(_parse_item(entry, default_date=default_date))
        except ValueError as exc:
            msg = f"items[{index}]: {exc}"
            raise ValueError(msg) from exc
    exported_at = raw.get("exported_at")
    return FoodLogTransferPayload(
        default_date=default_date,
        items=items,
        exported_at=str(exported_at) if exported_at else None,
    )
```

</details>

## 🔧 Function `payload_dict`

```python
def payload_dict(default_date: str, items: list[FoodLogTransferItem], *, exported_at: str) -> dict[str, Any]
```

Serialize one day of items to the transfer JSON object.

<details>
<summary>Code:</summary>

```python
def payload_dict(default_date: str, items: list[FoodLogTransferItem], *, exported_at: str) -> dict[str, Any]:
    return {
        "format": FORMAT_ID,
        "version": FORMAT_VERSION,
        "exported_at": exported_at,
        "default_date": default_date,
        "items": [item_to_json(item) for item in items],
    }
```

</details>

## 🔧 Function `transfer_filename_for_date`

```python
def transfer_filename_for_date(day: str) -> str
```

Return `food-log-YYYY-MM-DD.json` for a calendar day.

<details>
<summary>Code:</summary>

```python
def transfer_filename_for_date(day: str) -> str:
    return f"{FILE_NAME_PREFIX}{day}.json"
```

</details>

## 🔧 Function `transfer_items_to_parsed`

```python
def transfer_items_to_parsed(items: list[FoodLogTransferItem], *, default_date: str) -> list[ParsedFoodItem]
```

Convert transfer items to [`ParsedFoodItem`](text_parser.g.md#%EF%B8%8F-class-parsedfooditem) (uses each item date or `default_date`).

<details>
<summary>Code:</summary>

```python
def transfer_items_to_parsed(
    items: list[FoodLogTransferItem],
    *,
    default_date: str,
) -> list[ParsedFoodItem]:
    parsed: list[ParsedFoodItem] = []
    for item in items:
        day = item.date if _DATE_RE.match(item.date) else default_date
        parsed.append(
            ParsedFoodItem(
                name=item.name,
                weight=item.weight,
                calories_per_100g=item.calories_per_100g,
                portion_calories=None,
                food_date=day,
                is_drink=item.is_drink,
            )
        )
    return parsed
```

</details>

## 🔧 Function `write_transfer_files`

```python
def write_transfer_files(items: list[FoodLogTransferItem], *, directory: Path | None = None, single_path: Path | None = None) -> list[Path]
```

Write one JSON file per date.

Args:

- `items` (`list[FoodLogTransferItem]`): Rows to export.
- `directory` (`Path | None`): Target folder for multi-date export.
- `single_path` (`Path | None`): Exact path when exporting a single date.

Returns:

- `list[Path]`: Written file paths.

<details>
<summary>Code:</summary>

```python
def write_transfer_files(
    items: list[FoodLogTransferItem],
    *,
    directory: Path | None = None,
    single_path: Path | None = None,
) -> list[Path]:
    grouped = group_items_by_date(items)
    if not grouped:
        return []
    exported_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    written: list[Path] = []
    if len(grouped) == 1 and single_path is not None:
        day, day_items = next(iter(grouped.items()))
        single_path.parent.mkdir(parents=True, exist_ok=True)
        single_path.write_text(
            json.dumps(payload_dict(day, day_items, exported_at=exported_at), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return [single_path]
    if directory is None:
        msg = "directory is required when exporting multiple dates (or without single_path)"
        raise ValueError(msg)
    directory.mkdir(parents=True, exist_ok=True)
    for day in sorted(grouped):
        path = unique_path_in_folder(directory, f"{FILE_NAME_PREFIX}{day}", ".json")
        path.write_text(
            json.dumps(payload_dict(day, grouped[day], exported_at=exported_at), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        written.append(path)
    return written
```

</details>
