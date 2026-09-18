"""JSON transfer format for food log rows (export / import without AI).

Files use format ID `harrix-food-log` and are typically named `food-log-YYYY-MM-DD.json`.

"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from harrix_swiss_knife.apps.common.widgets.path_drop_helpers import unique_path_in_folder
from harrix_swiss_knife.apps.food.food_log_calories import (
    convert_portion_to_calories_per_100g,
    effective_calories_per_100g,
)
from harrix_swiss_knife.apps.food.text_parser import ParsedFoodItem

FORMAT_ID = "harrix-food-log"
FORMAT_VERSION = 1
FILE_NAME_PREFIX = "food-log-"
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

CalorieModeJson = Literal["weight", "portion"]


@dataclass(frozen=True, slots=True)
class FoodLogTransferItem:
    """One food log row ready for JSON transfer or dialog preview."""

    name: str
    weight: float
    is_drink: bool
    calories_per_100g: float | None
    date: str
    name_en: str | None = None


@dataclass(frozen=True, slots=True)
class FoodLogTransferPayload:
    """Parsed transfer file contents."""

    default_date: str
    items: list[FoodLogTransferItem]
    exported_at: str | None = None


def build_transfer_item_from_log_row(
    *,
    date: str,
    name: str,
    name_en: str | None,
    weight: float | None,
    calories_per_100g: float | None,
    is_drink: bool,
) -> FoodLogTransferItem | None:
    """Build a transfer item from a food_log DB row, or `None` when incomplete."""
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


def group_items_by_date(items: list[FoodLogTransferItem]) -> dict[str, list[FoodLogTransferItem]]:
    """Group transfer items by `date` (sorted keys when iterated via `sorted`)."""
    grouped: dict[str, list[FoodLogTransferItem]] = {}
    for item in items:
        grouped.setdefault(item.date, []).append(item)
    return grouped


def is_food_log_transfer_path(file_path: str | Path) -> bool:
    """Return `True` when path looks like a transfer JSON file by suffix."""
    return Path(file_path).suffix.lower() == ".json"


def item_to_json(item: FoodLogTransferItem) -> dict[str, Any]:
    """Serialize one transfer item (always weight / kcal per 100 g)."""
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


def items_to_tsv(items: list[FoodLogTransferItem]) -> str:
    """Convert transfer items to FoodTableDialog TSV (Name/Weight/Calories/Mode/Drink)."""
    lines: list[str] = []
    for item in items:
        calories = item.calories_per_100g or 0
        drink = "yes" if item.is_drink else "no"
        lines.append(f"{item.name}\t{item.weight:g}\t{calories:g}\tweight\t{drink}")
    return "\n".join(lines)


def name_en_lookup(items: list[FoodLogTransferItem]) -> dict[str, str]:
    """Map casefolded name → English name from transfer items."""
    result: dict[str, str] = {}
    for item in items:
        if item.name_en:
            result[item.name.casefold()] = item.name_en
    return result


def parse_transfer_file(path: Path) -> FoodLogTransferPayload:
    """Load and validate a transfer JSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return parse_transfer_payload(raw)


def parse_transfer_payload(raw: Any) -> FoodLogTransferPayload:
    """Validate a transfer JSON object."""
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


def parsed_items_to_transfer(
    items: list[ParsedFoodItem],
    *,
    default_date: str,
    name_en_by_name: dict[str, str] | None = None,
) -> list[FoodLogTransferItem]:
    """Convert dialog `ParsedFoodItem` rows to transfer items for JSON export."""
    result: list[FoodLogTransferItem] = []
    for item in items:
        if item.weight is None or item.weight <= 0:
            continue
        calories_per_100g = effective_calories_per_100g(
            item.calories_per_100g,
            portion_calories=item.portion_calories,
            weight=item.weight,
        )
        if calories_per_100g is None or calories_per_100g < 0:
            continue
        day = (item.food_date or default_date).strip()[:10]
        if not _DATE_RE.match(day):
            day = default_date
        name_en = None
        if name_en_by_name:
            name_en = name_en_by_name.get(item.name.casefold())
        built = build_transfer_item_from_log_row(
            date=day,
            name=item.name,
            name_en=name_en,
            weight=item.weight,
            calories_per_100g=calories_per_100g,
            is_drink=item.is_drink,
        )
        if built is not None:
            result.append(built)
    return result


def payload_dict(default_date: str, items: list[FoodLogTransferItem], *, exported_at: str) -> dict[str, Any]:
    """Serialize one day of items to the transfer JSON object."""
    return {
        "format": FORMAT_ID,
        "version": FORMAT_VERSION,
        "exported_at": exported_at,
        "default_date": default_date,
        "items": [item_to_json(item) for item in items],
    }


def transfer_filename_for_date(day: str) -> str:
    """Return `food-log-YYYY-MM-DD.json` for a calendar day."""
    return f"{FILE_NAME_PREFIX}{day}.json"


def transfer_items_to_parsed(
    items: list[FoodLogTransferItem],
    *,
    default_date: str,
) -> list[ParsedFoodItem]:
    """Convert transfer items to `ParsedFoodItem` (uses each item date or `default_date`)."""
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


def write_transfer_files(
    items: list[FoodLogTransferItem],
    *,
    directory: Path | None = None,
    single_path: Path | None = None,
) -> list[Path]:
    """Write one JSON file per date.

    Args:

    - `items` (`list[FoodLogTransferItem]`): Rows to export.
    - `directory` (`Path | None`): Target folder for multi-date export.
    - `single_path` (`Path | None`): Exact path when exporting a single date.

    Returns:

    - `list[Path]`: Written file paths.

    """
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


def _optional_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_name(value: str | None) -> str | None:
    text = (value or "").strip()
    return text or None


def _parse_item(entry: Any, *, default_date: str) -> FoodLogTransferItem:
    if not isinstance(entry, dict):
        msg = "item must be an object"
        raise TypeError(msg)
    name = str(entry.get("name") or "").strip()
    if not name:
        msg = "name is required"
        raise ValueError(msg)
    try:
        weight = float(entry.get("weight"))
    except (TypeError, ValueError) as exc:
        msg = "weight must be a number"
        raise ValueError(msg) from exc
    if weight <= 0:
        msg = "weight must be > 0"
        raise ValueError(msg)
    day = str(entry.get("date") or default_date).strip()[:10]
    if not _DATE_RE.match(day):
        msg = "date must be YYYY-MM-DD"
        raise ValueError(msg)
    mode_raw = str(entry.get("calorie_mode") or "").strip().lower()
    calories_per_100g = _optional_float(entry.get("calories_per_100g"))
    portion_calories = _optional_float(entry.get("portion_calories"))
    if mode_raw in {"weight", "per_100g"}:
        if calories_per_100g is None or calories_per_100g < 0:
            msg = "calories_per_100g is required for weight mode"
            raise ValueError(msg)
    elif mode_raw == "portion" or (portion_calories is not None and portion_calories > 0):
        if portion_calories is None or portion_calories <= 0:
            msg = "portion_calories must be > 0 for portion mode"
            raise ValueError(msg)
        calories_per_100g = convert_portion_to_calories_per_100g(
            weight=weight,
            portion_calories=portion_calories,
        )
    elif calories_per_100g is not None and calories_per_100g >= 0:
        pass
    else:
        msg = "calories_per_100g or portion_calories is required"
        raise ValueError(msg)
    is_drink = bool(entry.get("is_drink"))
    return FoodLogTransferItem(
        name=name,
        name_en=_optional_name(entry.get("name_en") if isinstance(entry.get("name_en"), str) else None),
        weight=weight,
        is_drink=is_drink,
        calories_per_100g=calories_per_100g,
        date=day,
    )
