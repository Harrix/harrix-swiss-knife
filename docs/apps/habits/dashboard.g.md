---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `dashboard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitDashboardWidget`](#%EF%B8%8F-class-habitdashboardwidget)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `add_habit`](#%EF%B8%8F-method-add_habit)
  - [⚙️ Method `refresh`](#%EF%B8%8F-method-refresh)
  - [⚙️ Method `set_database`](#%EF%B8%8F-method-set_database)

</details>

## 🏛️ Class `HabitDashboardWidget`

```python
class HabitDashboardWidget(QWidget)
```

Master-detail habits dashboard matching the design TZ screenshot.

<details>
<summary>Code:</summary>

```python
class HabitDashboardWidget(QWidget):

    data_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._selected_habit_id: int | None = None
        today = _local_today()
        self._calendar_year = today.year
        self._calendar_month = today.month
        self._week_dates: list[date] = []
        self._habit_rows: dict[int, HabitRow] = {}

        self.setStyleSheet("HabitDashboardWidget { background: #FFFFFF; }")
        self._build_ui()

    def add_habit(self) -> None:
        """Prompt for a habit and add it to the database."""
        if self._db is None:
            return
        dialog = HabitEditDialog(self, title="Add Habit")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if self._db.add_habit(dialog.habit_name(), is_bool=dialog.habit_is_bool(), emoji=dialog.habit_emoji()):
            self.refresh()
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Database Error", "Failed to add habit.")

    def refresh(self) -> None:
        """Reload list, week rings, and detail pane from the database."""
        if self._db is None:
            self._clear_habit_list()
            self._show_empty_detail()
            return

        self._week_dates = _last_seven_days(_local_today())
        self._update_week_bar()
        self._rebuild_habit_list()
        self._refresh_detail()

    def set_database(self, db_manager: DatabaseManager | None) -> None:
        """Attach database manager and refresh."""
        self._db = db_manager
        self.refresh()

    def _build_left_pane(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("habitDashLeft")
        pane.setStyleSheet(
            """
            QFrame#habitDashLeft {
                background: #FFFFFF;
                border-right: 1px solid #E5E7EB;
            }
            """
        )
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Habit")
        title.setStyleSheet("color: #111827; font-size: 20px; font-weight: 700;")
        header.addWidget(title)
        layout.addLayout(header)

        week_row = QHBoxLayout()
        week_row.setSpacing(4)
        self._week_headers: list[WeekDayHeader] = []
        for _ in range(7):
            cell = WeekDayHeader()
            self._week_headers.append(cell)
            week_row.addWidget(cell, 1)
        layout.addLayout(week_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._list_host = QWidget()
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._list_layout.addStretch(1)
        scroll.setWidget(self._list_host)
        layout.addWidget(scroll, 1)
        return pane

    def _build_right_pane(self) -> QWidget:
        pane = QFrame()
        pane.setObjectName("habitDashRight")
        pane.setStyleSheet("QFrame#habitDashRight { background: #FFFFFF; }")
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(14)

        header = QHBoxLayout()
        self._detail_icon = HabitIconBadge(size=44)
        self._detail_name = QLabel("Select a habit")
        self._detail_name.setStyleSheet("color: #111827; font-size: 16px; font-weight: 700;")
        self._detail_name.setWordWrap(True)
        header.addWidget(self._detail_icon)
        header.addWidget(self._detail_name, 1)
        self._detail_more = QPushButton("⋯")
        self._detail_more.setFixedSize(32, 32)
        self._detail_more.setCursor(Qt.CursorShape.PointingHandCursor)
        self._detail_more.setStyleSheet(
            """
            QPushButton {
                background: transparent; border: none; color: #6B7280;
                font-size: 16px; border-radius: 8px;
            }
            QPushButton:hover { background: #F3F4F6; color: #111827; }
            """
        )
        self._detail_more.clicked.connect(self._on_detail_menu)
        header.addWidget(self._detail_more)
        layout.addLayout(header)

        stats = QGridLayout()
        stats.setSpacing(10)
        self._stat_monthly = StatCard("Monthly check-ins", "✓", COLOR_SUCCESS)
        self._stat_total = StatCard("Total check-ins", "⚡", COLOR_PRIMARY)
        self._stat_rate = StatCard("Monthly check-in rate", "%", COLOR_RATE)
        self._stat_streak = StatCard("Streak", "🔥", COLOR_STREAK)
        stats.addWidget(self._stat_monthly, 0, 0)
        stats.addWidget(self._stat_total, 0, 1)
        stats.addWidget(self._stat_rate, 1, 0)
        stats.addWidget(self._stat_streak, 1, 1)
        layout.addLayout(stats)

        self._calendar = MonthCalendarGrid()
        self._calendar.day_toggled.connect(self._on_calendar_day_toggled)
        self._calendar.month_changed.connect(self._on_calendar_month_changed)
        layout.addWidget(self._calendar)

        log_title = QLabel("Habit Log on —.")
        log_title.setObjectName("habitLogTitle")
        log_title.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        self._log_title = log_title
        layout.addWidget(log_title)

        self._log_placeholder = QLabel("No check-in thoughts to share this month yet.")
        self._log_placeholder.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        self._log_placeholder.setWordWrap(True)
        layout.addWidget(self._log_placeholder)
        layout.addStretch(1)
        return pane

    # --- UI construction -------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter)

        left = self._build_left_pane()
        right = self._build_right_pane()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([720, 480])

    def _clear_habit_list(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._habit_rows.clear()

    def _edit_selected_habit(self) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        habit = self._db.get_habit_by_id(self._selected_habit_id)
        if habit is None:
            return
        habit_id = int(habit[0])
        name = str(habit[_NAME_COLUMN] or "")
        is_bool = bool(habit[_IS_BOOL_COLUMN] == 1) if len(habit) > _IS_BOOL_COLUMN else True
        emoji = normalize_habit_emoji(
            str(habit[_EMOJI_COLUMN]) if len(habit) > _EMOJI_COLUMN else "", habit_id=habit_id
        )
        dialog = HabitEditDialog(
            self,
            title="Edit Habit",
            name=name,
            is_bool=is_bool,
            emoji=emoji,
            habit_id=habit_id,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if self._db.update_habit(
            habit_id,
            dialog.habit_name(),
            is_bool=dialog.habit_is_bool(),
            emoji=dialog.habit_emoji(),
        ):
            self.refresh()
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Database Error", "Failed to update habit.")

    def _on_calendar_day_toggled(self, date_str: str) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        self._toggle_date(self._selected_habit_id, date_str)

    def _on_calendar_month_changed(self, year: int, month: int) -> None:
        self._calendar_year = year
        self._calendar_month = month
        self._refresh_detail()

    def _on_detail_menu(self) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        menu = QMenu(self)
        act_edit = menu.addAction("Edit habit")
        act_archive = menu.addAction("Archive habit")
        act_delete = menu.addAction("Delete habit")
        chosen = menu.exec_(self._detail_more.mapToGlobal(self._detail_more.rect().bottomLeft()))
        habit_id = self._selected_habit_id
        if chosen == act_edit:
            self._edit_selected_habit()
        elif chosen == act_archive:
            if self._db.set_habit_archived(habit_id, is_archived=True):
                self._selected_habit_id = None
                self.refresh()
                self.data_changed.emit()
        elif chosen == act_delete:
            reply = QMessageBox.question(
                self,
                "Delete Habit",
                "Delete this habit and all of its check-ins?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Delete process records first, then habit
                self._db.execute_simple_query(
                    "DELETE FROM process_habits WHERE _id_habit = :id",
                    {"id": habit_id},
                )
                if self._db.delete_habit(habit_id):
                    self._selected_habit_id = None
                    self.refresh()
                    self.data_changed.emit()

    # --- Interactions ----------------------------------------------------

    def _on_habit_selected(self, habit_id: int) -> None:
        self._selected_habit_id = habit_id
        for hid, row in self._habit_rows.items():
            # Re-apply selection style without full rebuild
            week_done = [
                self._db.is_habit_done_on_date(hid, d.isoformat()) if self._db else False for d in self._week_dates
            ]
            habit = self._db.get_habit_by_id(hid) if self._db else None
            name = str(habit[_NAME_COLUMN]) if habit else ""
            emoji = (
                normalize_habit_emoji(str(habit[_EMOJI_COLUMN]) if len(habit) > _EMOJI_COLUMN else "", habit_id=hid)
                if habit
                else ""
            )
            total = self._db.get_habit_total_checkins(hid) if self._db else 0
            streak = self._db.get_habit_streak(hid) if self._db else 0
            row.set_habit_data(
                hid,
                name,
                total,
                streak,
                week_done,
                selected=hid == habit_id,
                emoji=emoji,
            )
        self._refresh_detail()

    def _on_week_day_toggled(self, habit_id: int, day_index: int) -> None:
        if self._db is None or day_index < 0 or day_index >= len(self._week_dates):
            return
        self._selected_habit_id = habit_id
        day = self._week_dates[day_index]
        self._toggle_date(habit_id, day.isoformat())

    def _rebuild_habit_list(self) -> None:
        if self._db is None:
            return
        self._clear_habit_list()
        habits = self._db.get_habits(include_archived=False)
        if not habits:
            empty = QLabel("No habits yet. Use Commands → Add habit to add one.")
            empty.setStyleSheet("color: #9CA3AF; font-size: 13px; padding: 24px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.insertWidget(0, empty)
            self._selected_habit_id = None
            return

        habit_ids = [int(row[0]) for row in habits]
        if self._selected_habit_id not in habit_ids:
            self._selected_habit_id = habit_ids[0]

        for row in habits:
            habit_id = int(row[0])
            name = str(row[_NAME_COLUMN])
            emoji = normalize_habit_emoji(
                str(row[_EMOJI_COLUMN]) if len(row) > _EMOJI_COLUMN else "",
                habit_id=habit_id,
            )
            total_days = self._db.get_habit_total_checkins(habit_id)
            streak = self._db.get_habit_streak(habit_id)
            week_done = [self._db.is_habit_done_on_date(habit_id, d.isoformat()) for d in self._week_dates]
            habit_row = HabitRow()
            habit_row.set_habit_data(
                habit_id,
                name,
                total_days,
                streak,
                week_done,
                selected=habit_id == self._selected_habit_id,
                emoji=emoji,
            )
            habit_row.selected.connect(self._on_habit_selected)
            habit_row.day_toggled.connect(self._on_week_day_toggled)
            self._habit_rows[habit_id] = habit_row
            self._list_layout.insertWidget(self._list_layout.count() - 1, habit_row)

    def _refresh_detail(self) -> None:
        if self._db is None or self._selected_habit_id is None:
            self._show_empty_detail()
            return

        habit = self._db.get_habit_by_id(self._selected_habit_id)
        if habit is None:
            self._show_empty_detail()
            return

        habit_id = int(habit[0])
        name = str(habit[_NAME_COLUMN])
        emoji = normalize_habit_emoji(
            str(habit[_EMOJI_COLUMN]) if len(habit) > _EMOJI_COLUMN else "",
            habit_id=habit_id,
        )
        self._detail_icon.set_habit(habit_id, emoji)
        self._detail_name.setText(name)

        year, month = self._calendar_year, self._calendar_month
        month_start = f"{year:04d}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        month_end = f"{year:04d}-{month:02d}-{last_day:02d}"
        today = _local_today()
        # Rate uses days elapsed in month (up to today for current month)
        if year == today.year and month == today.month:
            days_in_period = today.day
        elif (year, month) > (today.year, today.month):
            days_in_period = 0
        else:
            days_in_period = last_day

        monthly = self._db.count_habit_checkins_between(habit_id, month_start, month_end)
        total = self._db.get_habit_total_checkins(habit_id)
        streak = self._db.get_habit_streak(habit_id)
        rate = round(100 * monthly / days_in_period) if days_in_period > 0 else 0

        self._stat_monthly.set_value(f"{monthly} Days")
        self._stat_total.set_value(f"{total} Days")
        self._stat_rate.set_value(f"{rate}%")
        self._stat_streak.set_value(f"{streak} Days")

        done_dates = set(self._db.get_habit_done_dates_between(habit_id, month_start, month_end))
        self._calendar.set_month(year, month, done_dates)
        self._log_title.setText(f"Habit Log on {_month_name(month)}.")

    def _show_empty_detail(self) -> None:
        self._detail_name.setText("Select a habit")
        self._stat_monthly.set_value("-")
        self._stat_total.set_value("-")
        self._stat_rate.set_value("-")
        self._stat_streak.set_value("-")
        today = _local_today()
        self._calendar.set_month(today.year, today.month, set())
        self._log_title.setText(f"Habit Log on {_month_name(today.month)}.")

    def _toggle_date(self, habit_id: int, date_str: str) -> None:
        if self._db is None:
            return
        ok = self._db.toggle_habit_checkin(habit_id, date_str)
        if not ok:
            QMessageBox.warning(self, "Database Error", "Failed to toggle check-in.")
            return
        self.refresh()
        self.data_changed.emit()

    # --- Data refresh ----------------------------------------------------

    def _update_week_bar(self) -> None:
        if self._db is None:
            return
        today = _local_today()
        habits = self._db.get_habits(include_archived=False)
        habit_ids = [int(row[0]) for row in habits]
        total = len(habit_ids)
        for i, day in enumerate(self._week_dates):
            caption = f"{weekday_short(day.weekday())} {day.day}"
            if total == 0:
                ratio = 0.0
            else:
                done = sum(1 for hid in habit_ids if self._db.is_habit_done_on_date(hid, day.isoformat()))
                ratio = done / total
            self._week_headers[i].set_day(caption, ratio, is_today=day == today)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._selected_habit_id: int | None = None
        today = _local_today()
        self._calendar_year = today.year
        self._calendar_month = today.month
        self._week_dates: list[date] = []
        self._habit_rows: dict[int, HabitRow] = {}

        self.setStyleSheet("HabitDashboardWidget { background: #FFFFFF; }")
        self._build_ui()
```

</details>

### ⚙️ Method `add_habit`

```python
def add_habit(self) -> None
```

Prompt for a habit and add it to the database.

<details>
<summary>Code:</summary>

```python
def add_habit(self) -> None:
        if self._db is None:
            return
        dialog = HabitEditDialog(self, title="Add Habit")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if self._db.add_habit(dialog.habit_name(), is_bool=dialog.habit_is_bool(), emoji=dialog.habit_emoji()):
            self.refresh()
            self.data_changed.emit()
        else:
            QMessageBox.warning(self, "Database Error", "Failed to add habit.")
```

</details>

### ⚙️ Method `refresh`

```python
def refresh(self) -> None
```

Reload list, week rings, and detail pane from the database.

<details>
<summary>Code:</summary>

```python
def refresh(self) -> None:
        if self._db is None:
            self._clear_habit_list()
            self._show_empty_detail()
            return

        self._week_dates = _last_seven_days(_local_today())
        self._update_week_bar()
        self._rebuild_habit_list()
        self._refresh_detail()
```

</details>

### ⚙️ Method `set_database`

```python
def set_database(self, db_manager: DatabaseManager | None) -> None
```

Attach database manager and refresh.

<details>
<summary>Code:</summary>

```python
def set_database(self, db_manager: DatabaseManager | None) -> None:
        self._db = db_manager
        self.refresh()
```

</details>
