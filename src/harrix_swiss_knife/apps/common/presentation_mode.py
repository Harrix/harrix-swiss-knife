"""Session-scoped presentation mode for tracker apps (fake temp SQLite)."""

from __future__ import annotations

import logging
import sqlite3
import tempfile
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget  # noqa: TC002

from harrix_swiss_knife.apps.common import message_box
from harrix_swiss_knife.apps.common.qt_database_manager_base import QtSqliteDatabaseManagerBase
from harrix_swiss_knife.qt_lucide_icon import apply_lucide_action_icon, apply_menu_icon_size

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

PresentationApp = Literal["finance", "fitness", "food", "habits"]

PRESENTATION_TITLE_SUFFIX = " — Presentation mode"
PRESENTATION_MENU_LABEL = "Presentation mode"
OPEN_IN_PRESENTATION_MENU_LABEL = "Open in presentation mode"
PRESENTATION_ENTER_INFO = (
    "Presentation mode uses fake sample data in a temporary database.\nChanges will not be saved to your real database."
)

_APPS_PACKAGE = Path(__file__).resolve().parents[1]
_HISTORY_DAYS = 21
_FINANCE_HISTORY_DAYS = 60
_FINANCE_QUIET_DAY_MOD = 11
_FINANCE_QUIET_DAY_REMAINDER = 10
_HABIT_SKIP_MOD = 3
_HABIT_SKIP_REMAINDER = 2


def apply_presentation_window_title(window: QWidget, *, enabled: bool) -> None:
    """Set or clear the presentation-mode suffix on the window title and caption."""
    stored = getattr(window, "_presentation_base_title", None)
    if not isinstance(stored, str) or not stored.strip():
        stored = strip_presentation_title_suffix(window.windowTitle())
        window._presentation_base_title = stored  # noqa: SLF001
    title = f"{stored}{PRESENTATION_TITLE_SUFFIX}" if enabled else stored
    window.setWindowTitle(title)
    try:
        from harrix_swiss_knife.win11_caption import refresh_win11_caption  # noqa: PLC0415

        refresh_win11_caption(window)
    except Exception:
        logger.debug("Could not refresh caption after presentation title change", exc_info=True)


def create_presentation_database(app: PresentationApp) -> Path:
    """Create a temp SQLite DB from `recover.sql` plus synthetic rows including today.

    Args:

    - `app` (`PresentationApp`): Tracker app ID.

    Returns:

    - `Path`: Path to the new `{app}.db` under a temp folder.

    Raises:

    - `FileNotFoundError`: When `recover.sql` is missing.
    - `RuntimeError`: When the database file cannot be created.

    """
    recover = _recover_sql_path(app)
    if not recover.is_file():
        msg = f"recover.sql not found for {app}: {recover}"
        raise FileNotFoundError(msg)

    folder = Path(tempfile.mkdtemp(prefix=f"hsk_presentation_{app}_"))
    db_path = folder / f"{app}.db"
    ok = QtSqliteDatabaseManagerBase.create_database_from_sql(str(db_path), str(recover))
    if not ok or not db_path.is_file():
        msg = f"Failed to create presentation database for {app}"
        raise RuntimeError(msg)

    seeders: dict[PresentationApp, Callable[[Path], None]] = {
        "finance": _seed_finance,
        "fitness": _seed_fitness,
        "food": _seed_food,
        "habits": _seed_habits,
    }
    seeders[app](db_path)
    if app == "food":
        from harrix_swiss_knife.apps.food.schema import (  # noqa: PLC0415
            ensure_food_indexes,
            ensure_food_schema,
        )

        ensure_food_schema(db_path)
        ensure_food_indexes(db_path)
    return db_path


def install_presentation_mode_action(
    window: QWidget,
    menu: QMenu | None,
    *,
    get_enabled: Callable[[], bool],
    set_enabled: Callable[..., None],
) -> QAction | None:
    """Add a checkable Commands → Presentation mode action.

    Args:

    - `window` (`QWidget`): Host window (parent of the action).
    - `menu` (`QMenu | None`): Commands menu; no-op when missing.
    - `get_enabled` (`Callable[[], bool]`): Current presentation flag.
    - `set_enabled` (`Callable[..., None]`): Apply the new flag (`enabled=`).

    Returns:

    - `QAction | None`: Created action, or `None` when `menu` is missing.

    """
    if menu is None:
        return None
    action = QAction(PRESENTATION_MENU_LABEL, window)
    action.setCheckable(True)
    action.setChecked(get_enabled())
    apply_lucide_action_icon(action, "presentation")
    apply_menu_icon_size(menu)

    def _on_triggered(*, checked: bool) -> None:
        if checked == get_enabled():
            return
        if checked:
            message_box.information(window, PRESENTATION_MENU_LABEL, PRESENTATION_ENTER_INFO)
        try:
            set_enabled(enabled=checked)
        except Exception as exc:
            logger.exception("Failed to toggle presentation mode")
            action.blockSignals(True)  # noqa: FBT003
            action.setChecked(get_enabled())
            action.blockSignals(False)  # noqa: FBT003
            message_box.warning(window, PRESENTATION_MENU_LABEL, str(exc))
            return
        action.blockSignals(True)  # noqa: FBT003
        action.setChecked(get_enabled())
        action.blockSignals(False)  # noqa: FBT003

    action.triggered.connect(lambda checked: _on_triggered(checked=checked))
    menu.addSeparator()
    menu.addAction(action)
    window._presentation_mode_action = action  # noqa: SLF001
    return action


def presentation_ticktick_db_path(habits_db_path: Path) -> Path:
    """Return the synthetic TickTick DB next to a habits presentation database."""
    return habits_db_path.parent / "TickTick.db"


def strip_presentation_title_suffix(title: str) -> str:
    """Return `title` without the presentation-mode suffix."""
    text = title.strip()
    if text.endswith(PRESENTATION_TITLE_SUFFIX):
        return text[: -len(PRESENTATION_TITLE_SUFFIX)].rstrip()
    return text


def sync_presentation_mode_action(window: Any) -> None:
    """Update the check state of a previously installed presentation action."""
    action = getattr(window, "_presentation_mode_action", None)
    if not isinstance(action, QAction):
        return
    enabled = bool(getattr(window, "presentation_mode", False))
    action.blockSignals(True)  # noqa: FBT003
    action.setChecked(enabled)
    action.blockSignals(False)  # noqa: FBT003


def _date_iso(days_ago: int = 0) -> str:
    return (_today() - timedelta(days=days_ago)).isoformat()


def _recover_sql_path(app: PresentationApp) -> Path:
    return _APPS_PACKAGE / app / "recover.sql"


def _seed_finance(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        rub = conn.execute("SELECT _id FROM currencies WHERE code = 'RUB'").fetchone()
        usd = conn.execute("SELECT _id FROM currencies WHERE code = 'USD'").fetchone()
        category_rows = conn.execute(
            """
            SELECT name, _id FROM categories
            WHERE name IN (
                'Food', 'Cafe', 'Transport', 'Salary', 'Entertainment',
                'Healthcare', 'Utilities', 'Gifts', 'Freelance'
            )
            """
        ).fetchall()
        categories = {str(name): int(cid) for name, cid in category_rows}
        required = ("Food", "Cafe", "Transport", "Salary")
        if rub is None or any(name not in categories for name in required):
            msg = "Finance recover.sql is missing expected currencies/categories"
            raise RuntimeError(msg)
        rub_id = int(rub[0])
        usd_id = int(usd[0]) if usd else rub_id

        expense_templates = [
            ("Food", "Grocery store", -45000, "demo"),
            ("Food", "Supermarket", -78000, "demo"),
            ("Food", "Bakery", -28000, "demo"),
            ("Cafe", "Coffee shop", -32000, "demo"),
            ("Cafe", "Lunch with colleagues", -56000, "demo"),
            ("Transport", "Metro ride", -18000, "commute"),
            ("Transport", "Taxi to office", -25000, "commute"),
            ("Transport", "Bus ticket", -15000, "commute"),
            ("Entertainment", "Cinema tickets", -90000, "fun"),
            ("Healthcare", "Pharmacy", -42000, "health"),
            ("Utilities", "Internet bill", -89000, "home"),
            ("Gifts", "Birthday gift", -150000, "gift"),
        ]
        if "Entertainment" not in categories:
            expense_templates = [row for row in expense_templates if row[0] in categories]
        if "Healthcare" not in categories:
            expense_templates = [row for row in expense_templates if row[0] != "Healthcare"]
        if "Utilities" not in categories:
            expense_templates = [row for row in expense_templates if row[0] != "Utilities"]
        if "Gifts" not in categories:
            expense_templates = [row for row in expense_templates if row[0] != "Gifts"]

        for days_ago in range(_FINANCE_HISTORY_DAYS):
            # 1-3 expense rows most days; skip a few quiet days for variety.
            if days_ago % _FINANCE_QUIET_DAY_MOD == _FINANCE_QUIET_DAY_REMAINDER:
                continue
            day_count = 1 + (days_ago % 3)
            for offset in range(day_count):
                name, description, amount, tag = expense_templates[(days_ago + offset) % len(expense_templates)]
                _insert_finance_transaction(
                    conn,
                    amount=amount - (days_ago % 7) * 100,
                    description=description,
                    category_id=categories[name],
                    currency_id=rub_id,
                    days_ago=days_ago,
                    tag=tag,
                )
            # Payday near the start of each demo month window.
            if days_ago in {0, 30, 59}:
                _insert_finance_transaction(
                    conn,
                    amount=15000000,
                    description="Monthly salary",
                    category_id=categories["Salary"],
                    currency_id=rub_id,
                    days_ago=days_ago,
                    tag="income",
                )
            if "Freelance" in categories and days_ago in {14, 44}:
                _insert_finance_transaction(
                    conn,
                    amount=2500000,
                    description="Freelance project",
                    category_id=categories["Freelance"],
                    currency_id=rub_id,
                    days_ago=days_ago,
                    tag="income",
                )

        for days_ago in (0, 15, 30, 45):
            conn.execute(
                """
                INSERT INTO exchange_rates (_id_currency, rate, date)
                VALUES (?, ?, ?)
                """,
                (usd_id, 90.0 + (days_ago % 5) * 0.4, _date_iso(days_ago)),
            )
        if usd_id != rub_id:
            for days_ago in (2, 32):
                conn.execute(
                    """
                    INSERT INTO currency_exchanges
                        (_id_currency_from, _id_currency_to, amount_from, amount_to,
                         exchange_rate, fee, date, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (rub_id, usd_id, 1000000, 10800, 92.5, 0, _date_iso(days_ago), "Demo exchange"),
                )
        conn.execute("UPDATE accounts SET balance = 25000000 WHERE name = 'Bank Account'")
        conn.execute("UPDATE accounts SET balance = 150000 WHERE name = 'Cash'")
        conn.commit()


def _insert_finance_transaction(
    conn: sqlite3.Connection,
    *,
    amount: int,
    description: str,
    category_id: int,
    currency_id: int,
    days_ago: int,
    tag: str,
) -> None:
    conn.execute(
        """
        INSERT INTO transactions
            (amount, description, description_en, _id_categories, _id_currencies, date, tag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (amount, description, description, category_id, currency_id, _date_iso(days_ago), tag),
    )
    tx_id = int(conn.execute("SELECT last_insert_rowid()").fetchone()[0])
    conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
    tag_id = int(conn.execute("SELECT _id FROM tags WHERE name = ?", (tag,)).fetchone()[0])
    conn.execute(
        "INSERT OR IGNORE INTO transaction_tags (_id_transactions, _id_tags) VALUES (?, ?)",
        (tx_id, tag_id),
    )


def _seed_fitness(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        exercises = conn.execute(
            "SELECT _id, is_type_required FROM exercises WHERE name IN ('Push-ups', 'Squats', 'Pull-ups') ORDER BY _id"
        ).fetchall()
        if not exercises:
            exercises = conn.execute("SELECT _id, is_type_required FROM exercises ORDER BY _id LIMIT 3").fetchall()
        if not exercises:
            msg = "Fitness recover.sql has no exercises to seed"
            raise RuntimeError(msg)

        for days_ago in range(0, _HISTORY_DAYS, 2):
            for exercise_id, is_type_required in exercises:
                type_id = 0
                if int(is_type_required or 0) == 1:
                    row = conn.execute(
                        "SELECT _id FROM types WHERE _id_exercises = ? ORDER BY _id LIMIT 1",
                        (exercise_id,),
                    ).fetchone()
                    type_id = int(row[0]) if row else 0
                value = "20" if days_ago % 4 == 0 else "15"
                conn.execute(
                    "INSERT INTO process (_id_exercises, _id_types, value, date) VALUES (?, ?, ?, ?)",
                    (exercise_id, type_id, value, _date_iso(days_ago)),
                )

        base_weight = 72.0
        for days_ago in range(0, _HISTORY_DAYS, 3):
            conn.execute(
                "INSERT INTO weight (value, date) VALUES (?, ?)",
                (round(base_weight - days_ago * 0.05, 1), _date_iso(days_ago)),
            )
        conn.commit()


def _seed_food(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        items = conn.execute(
            """
            SELECT name, name_en, is_drink, calories_per_100g, default_portion_weight
            FROM food_items
            WHERE calories_per_100g IS NOT NULL
            ORDER BY _id
            LIMIT 8
            """
        ).fetchall()
        if not items:
            msg = "Food recover.sql has no food_items to seed"
            raise RuntimeError(msg)

        for days_ago in range(_HISTORY_DAYS):
            for offset in range(min(3, len(items))):
                name, name_en, is_drink, cal, portion = items[(days_ago + offset) % len(items)]
                weight = float(portion or 100.0)
                conn.execute(
                    """
                    INSERT INTO food_log
                        (date, weight, calories_per_100g, name, name_en, is_drink)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (_date_iso(days_ago), weight, float(cal or 100.0), name, name_en, int(is_drink or 0)),
                )
        conn.commit()


def _seed_habits(db_path: Path) -> None:
    with sqlite3.connect(str(db_path)) as conn:
        habits = [
            ("Morning stretch", 1, "🧘", "stretch-horizontal", 1),
            ("Read 20 pages", 1, "📖", "book-open", 2),
            ("Drink water", 0, "💧", "droplets", 3),
            ("Walk 5k steps", 1, "🚶", "footprints", 4),
        ]
        habit_ids: list[int] = []
        for name, is_bool, emoji, lucide, sort_order in habits:
            conn.execute(
                """
                INSERT INTO habits (name, is_bool, is_archived, emoji, icon_lucide, sort_order)
                VALUES (?, ?, 0, ?, ?, ?)
                """,
                (name, is_bool, emoji, lucide, sort_order),
            )
            habit_ids.append(int(conn.execute("SELECT last_insert_rowid()").fetchone()[0]))

        for days_ago in range(_HISTORY_DAYS):
            for index, habit_id in enumerate(habit_ids):
                if (days_ago + index) % _HABIT_SKIP_MOD == _HABIT_SKIP_REMAINDER:
                    continue
                is_bool = habits[index][1]
                value = 1 if is_bool else 2 + ((days_ago + index) % 4)
                conn.execute(
                    "INSERT INTO process_habits (_id_habit, value, date) VALUES (?, ?, ?)",
                    (habit_id, value, _date_iso(days_ago)),
                )
        conn.commit()

    ticktick_path = presentation_ticktick_db_path(db_path)
    _seed_ticktick_demo(ticktick_path)


def _seed_ticktick_demo(db_path: Path) -> None:
    """Write a tiny fake TickTick SQLite so the TickTick tab never reads the real file."""
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(
            """
            CREATE TABLE ProjectModel (
                id TEXT PRIMARY KEY,
                name TEXT,
                kind TEXT,
                closed INTEGER,
                delete_status INTEGER DEFAULT 0,
                sortOrder INTEGER DEFAULT 0
            );
            CREATE TABLE TaskModel (
                id TEXT PRIMARY KEY,
                projectId TEXT,
                title TEXT,
                completedTime TEXT,
                status INTEGER,
                deleted INTEGER DEFAULT 0
            );
            CREATE TABLE HabitModel (
                Id varchar,
                Name varchar,
                Type varchar,
                ArchivedTime datetime,
                CreatedTime datetime,
                TotalCheckIns INTEGER,
                SortOrder bigint
            );
            CREATE TABLE HabitCheckInModel (
                HabitId varchar,
                CheckinStamp varchar
            );
            """
        )
        completed_at = f"{_date_iso(0)}T12:00:00.000+0000"
        conn.execute(
            """
            INSERT INTO HabitModel
                (Id, Name, Type, ArchivedTime, CreatedTime, TotalCheckIns, SortOrder)
            VALUES ('demo1', 'Demo habit', 'Boolean', '', ?, 3, 1)
            """,
            (_date_iso(30) + " 10:00:00",),
        )
        for days_ago in (0, 1, 3):
            stamp = (_today() - timedelta(days=days_ago)).strftime("%Y%m%d")
            conn.execute(
                "INSERT INTO HabitCheckInModel (HabitId, CheckinStamp) VALUES ('demo1', ?)",
                (stamp,),
            )
        conn.execute(
            """
            INSERT INTO ProjectModel (id, name, kind, closed, delete_status, sortOrder)
            VALUES ('p1', 'Demo project', 'TASK', 0, 0, 1)
            """,
        )
        conn.execute(
            """
            INSERT INTO TaskModel (id, projectId, title, completedTime, status, deleted)
            VALUES ('t1', 'p1', 'Demo completed task', ?, 2, 0)
            """,
            (completed_at,),
        )
        conn.commit()


def _today() -> date:
    return datetime.now(UTC).astimezone().date()
