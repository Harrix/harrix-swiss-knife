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
    sport_habit_assign_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None, *, app_config: dict[str, Any] | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._selected_habit_id: int | None = None
        today = _local_today()
        self._calendar_year = today.year
        self._calendar_month = today.month
        self._week_dates: list[date] = []
        self._habit_rows: dict[int, HabitRow] = {}
        self._app_config: dict[str, Any] = app_config if app_config is not None else {}
        self._comments = HabitCommentsStore.from_config(self._app_config)
        self._comment_index: dict[int, set[str]] = {}
        # Per-refresh caches: without them one refresh costs ~10 queries per habit.
        self._habits_cache: list[list[Any]] | None = None
        self._stats_cache: dict[int, HabitStats] | None = None
        self._week_values_cache: dict[int, dict[str, int]] | None = None

        self.setAutoFillBackground(True)
        self.setStyleSheet("HabitDashboardWidget { background: #FFFFFF; }")
        self._build_ui()
        preload_habit_checkin_sounds()

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
        self._invalidate_caches()
        if self._db is None:
            self._comment_index = {}
            self._clear_habit_list()
            self._show_empty_detail()
            self._set_empty_state_visible(visible=True)
            return

        habits = self._habits()
        if not habits:
            self._week_dates = _last_seven_days(_local_today())
            self._comment_index = {}
            self._clear_habit_list()
            self._selected_habit_id = None
            self._show_empty_detail()
            self._set_empty_state_visible(visible=True)
            return

        self._set_empty_state_visible(visible=False)
        self._week_dates = _last_seven_days(_local_today())
        self._reload_comment_index()
        self._update_week_bar()
        self._rebuild_habit_list()
        self._refresh_detail()

    def set_database(self, db_manager: DatabaseManager | None) -> None:
        """Attach database manager and refresh."""
        self._db = db_manager
        self.refresh()

    def _after_checkin_changed(self, habit_id: int, *, sound_value: int | None) -> None:
        """Paint the new checkmark first, then sync tables and play sound."""
        self._invalidate_caches()
        self._update_week_bar()
        self._update_habit_row(habit_id)
        if self._selected_habit_id == habit_id:
            self._refresh_detail()
        play_habit_checkin_sound(sound_value)
        # Parent table reload is heavy; defer so the dashboard paints first.
        QTimer.singleShot(0, self.data_changed.emit)

    def _build_empty_state(self) -> QWidget:
        """Build a full-dashboard call-to-action shown when there are no habits."""
        pane = QFrame()
        pane.setObjectName("habitDashEmptyState")
        pane.setStyleSheet(
            """
            QFrame#habitDashEmptyState {
                background: #F8FAFC;
                border: 1px solid #E5E7EB;
                border-radius: 16px;
            }
            """
        )
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(16)

        title = QLabel("No habits yet")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #111827; font-size: 28px; font-weight: 800;")

        subtitle = QLabel("Add your first habit to start tracking days, streaks, and check-ins.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6B7280; font-size: 16px;")

        button = QPushButton("➕ Add habit")  # noqa: RUF001
        button.setObjectName("habitDashAddHabitButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumSize(280, 64)
        button.setStyleSheet(
            """
            QPushButton#habitDashAddHabitButton {
                background: #3B82F6;
                color: #FFFFFF;
                font-size: 20px;
                font-weight: 700;
                border: none;
                border-radius: 14px;
                padding: 16px 32px;
            }
            QPushButton#habitDashAddHabitButton:hover {
                background: #2563EB;
            }
            QPushButton#habitDashAddHabitButton:pressed {
                background: #1D4ED8;
            }
            """
        )
        button.clicked.connect(self.add_habit)

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(button, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        return pane

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
        scroll.setObjectName("habitDashListScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet(_LIST_SCROLL_STYLE)
        self._list_host = HabitRowListHost()
        self._list_host.habits_reordered.connect(self._on_habits_reordered)
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.addStretch(1)
        scroll.setWidget(self._list_host)
        scroll.viewport().setAutoFillBackground(True)
        scroll.viewport().setStyleSheet("background: #FFFFFF;")
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
        self._calendar.day_value_set.connect(self._on_calendar_day_value_set)
        self._calendar.day_comment_requested.connect(self._on_calendar_day_comment_requested)
        self._calendar.all_comments_requested.connect(self._show_all_comments)
        self._calendar.fill_absent_not_done.connect(self._on_calendar_fill_absent_not_done)
        self._calendar.month_changed.connect(self._on_calendar_month_changed)
        layout.addWidget(self._calendar)

        log_header = QHBoxLayout()
        log_title = QLabel("Habit Log on —.")
        log_title.setObjectName("habitLogTitle")
        log_title.setStyleSheet("color: #111827; font-size: 14px; font-weight: 700;")
        self._log_title = log_title
        log_header.addWidget(log_title, 1)
        self._all_comments_button = QPushButton("All comments…")
        self._all_comments_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._all_comments_button.setFlat(True)
        self._all_comments_button.setStyleSheet("color: #2563EB; font-size: 12px;")
        self._all_comments_button.clicked.connect(self._show_all_comments)
        log_header.addWidget(self._all_comments_button)
        layout.addLayout(log_header)

        self._log_placeholder = QLabel("No comments this month yet.")
        self._log_placeholder.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        self._log_placeholder.setWordWrap(True)
        layout.addWidget(self._log_placeholder)

        self._log_list = QListWidget()
        self._log_list.setObjectName("habitLogList")
        self._log_list.setMaximumHeight(160)
        self._log_list.itemActivated.connect(self._on_log_item_activated)
        self._log_list.hide()
        layout.addWidget(self._log_list)
        layout.addStretch(1)
        return pane

    # --- UI construction -------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("habitDashSplitter")
        splitter.setChildrenCollapsible(False)

        left = self._build_left_pane()
        right = self._build_right_pane()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([720, 480])

        self._stack = QStackedWidget()
        self._empty_state = self._build_empty_state()
        self._stack.addWidget(splitter)
        self._stack.addWidget(self._empty_state)
        root.addWidget(self._stack)
        self._set_empty_state_visible(visible=True)

    def _clear_habit_list(self) -> None:
        while self._list_layout.count() > 1:
            item = self._list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._habit_rows.clear()

    def _edit_day_comment(self, habit_id: int, date_str: str) -> None:
        """Open the editor for one habit-day comment and persist it."""
        if not self._ensure_comments_repository():
            return
        name = self._habit_display_name(habit_id)
        current = self._comments.comment(habit_id, date_str)
        dialog = HabitDayCommentDialog(self, habit_name=name, date_str=date_str, text=current)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        new_text = dialog.comment_text()
        if new_text == current:
            return
        if not current and not new_text:
            return
        self._comments.set_comment(habit_id, date_str, new_text, habit_name=name)
        self.refresh()

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

    def _ensure_comments_repository(self) -> bool:
        """Create Notes-Habits with Git when the comments folder is missing."""
        if not self._comments.is_configured():
            QMessageBox.warning(
                self,
                "Comments",
                "Habit comments folder is not configured. Set path_notes or path_habit_comments in config.json.",
            )
            return False
        root = self._comments.root()
        if root is None:
            return False
        created = not root.is_dir()
        if not self._comments.ensure_repository():
            QMessageBox.warning(self, "Comments", f"Could not create habit comments folder:\n{root}")
            return False
        if created and not str(self._app_config.get("path_habit_comments") or "").strip():
            persist_habit_comments_root(root, self._app_config)
        return True

    def _habit_display_name(self, habit_id: int) -> str:
        if self._db is None:
            return f"Habit {habit_id}"
        habit = self._db.get_habit_by_id(habit_id)
        if habit is None:
            return f"Habit {habit_id}"
        return str(habit[_NAME_COLUMN] or f"Habit {habit_id}")

    def _habit_name(self, habit_id: int) -> str:
        """Return the stored habit name, or empty when the habit is unknown."""
        for row in self._habits():
            if int(row[0]) == habit_id:
                return str(row[1] or "").strip()
        if self._db is not None:
            habit = self._db.get_habit_by_id(habit_id)
            if habit is not None:
                return str(habit[_NAME_COLUMN] or "").strip()
        return ""

    def _habit_stats(self, habit_id: int) -> HabitStats:
        """Return all-time totals for one habit, loading the whole map once per refresh."""
        if self._stats_cache is None:
            self._stats_cache = self._db.get_habit_stats_map() if self._db else {}
        return self._stats_cache.get(habit_id, HabitStats(total_checkins=0, streak=0))

    def _habits(self) -> list[list[Any]]:
        """Return active habits, loading them once per refresh."""
        if self._habits_cache is None:
            self._habits_cache = self._db.get_habits(include_archived=False) if self._db else []
        return self._habits_cache

    def _invalidate_caches(self) -> None:
        """Drop per-refresh caches so the next read reloads from the database."""
        self._habits_cache = None
        self._stats_cache = None
        self._week_values_cache = None

    def _on_calendar_day_comment_requested(self, date_str: str) -> None:
        if self._selected_habit_id is None:
            return
        self._edit_day_comment(self._selected_habit_id, date_str)

    def _on_calendar_day_toggled(self, date_str: str) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        self._toggle_date(self._selected_habit_id, date_str)

    def _on_calendar_day_value_set(self, date_str: str, value: object) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        self._set_date_value(self._selected_habit_id, date_str, value)

    def _on_calendar_fill_absent_not_done(self) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        habit_id = self._selected_habit_id
        year, month = self._calendar_year, self._calendar_month
        last_day = calendar.monthrange(year, month)[1]
        month_start = f"{year:04d}-{month:02d}-01"
        month_end = f"{year:04d}-{month:02d}-{last_day:02d}"
        day_values = self._db.get_habit_values_between(habit_id, month_start, month_end)
        dates = absent_dates_in_month(year, month, day_values, _local_today())
        if not dates:
            return
        try:
            self._db.upsert_habit_checkins([(habit_id, date_str, 0) for date_str in dates])
        except RuntimeError:
            QMessageBox.warning(self, "Database Error", "Failed to fill empty days.")
            return
        self._after_checkin_changed(habit_id, sound_value=0)

    def _on_calendar_month_changed(self, year: int, month: int) -> None:
        self._calendar_year = year
        self._calendar_month = month
        self._refresh_detail()

    def _on_detail_menu(self) -> None:
        if self._db is None or self._selected_habit_id is None:
            return
        menu = QMenu(self)
        act_edit = add_emoji_action(menu, "Edit habit", "✏️")
        act_comments = add_emoji_action(menu, "All comments…", "💬")
        act_archive = add_emoji_action(menu, "Archive habit", "🗄")
        act_delete = add_emoji_action(menu, "Delete habit", "🗑️")
        chosen = menu.exec_(self._detail_more.mapToGlobal(self._detail_more.rect().bottomLeft()))
        habit_id = self._selected_habit_id
        if chosen == act_edit:
            self._edit_selected_habit()
        elif chosen == act_comments:
            self._show_all_comments()
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

    def _on_habit_edit_requested(self, habit_id: int) -> None:
        self._on_habit_selected(habit_id)
        self._edit_selected_habit()

    def _on_habit_row_context_menu(self, habit_id: int, global_pos: QPoint) -> None:
        if self._selected_habit_id != habit_id:
            self._on_habit_selected(habit_id)
        HabitDayPickerPopup.hide_active()
        QToolTip.hideText()
        menu = QMenu(self)
        act_edit = add_emoji_action(menu, "Edit habit", "✏️")
        act_comments = add_emoji_action(menu, "All comments…", "💬")
        act_sport = None
        habit_name = self._habit_name(habit_id)
        if habit_name and not habit_names_match(habit_name, get_habits_sport_habit_name(self._app_config)):
            act_sport = add_emoji_action(menu, "Assign as sport habit", "🏃")
        chosen = menu.exec_(global_pos)
        if chosen == act_edit:
            self._edit_selected_habit()
        elif chosen == act_comments:
            self._show_all_comments()
        elif act_sport is not None and chosen == act_sport:
            self.sport_habit_assign_requested.emit(habit_name)

    def _on_habit_selected(self, habit_id: int) -> None:
        self._selected_habit_id = habit_id
        habits_by_id = {int(row[0]): row for row in self._habits()}
        for hid, row in self._habit_rows.items():
            # Re-apply selection style without full rebuild
            habit = habits_by_id.get(hid)
            name = str(habit[_NAME_COLUMN]) if habit else ""
            emoji = (
                normalize_habit_emoji(str(habit[_EMOJI_COLUMN]) if len(habit) > _EMOJI_COLUMN else "", habit_id=hid)
                if habit
                else ""
            )
            stats = self._habit_stats(hid)
            row.set_habit_data(
                hid,
                name,
                stats.total_checkins,
                stats.streak,
                self._week_values_for(hid),
                selected=hid == habit_id,
                emoji=emoji,
                allows_number=_habit_allows_number(habit),
                week_comments=self._week_comments_for(hid),
                week_dates=self._week_dates,
            )
        self._refresh_detail()

    def _on_habits_reordered(self, habit_ids: object) -> None:
        if self._db is None or not isinstance(habit_ids, list):
            return
        ordered_ids = [int(habit_id) for habit_id in habit_ids]
        if not ordered_ids:
            return
        if not self._db.reorder_habits(ordered_ids):
            QMessageBox.warning(self, "Database Error", "Failed to save habit order.")
            return
        self._invalidate_caches()
        self._rebuild_habit_list()
        self.data_changed.emit()

    def _on_log_item_activated(self, item: QListWidgetItem) -> None:
        date_str = item.data(Qt.ItemDataRole.UserRole)
        if self._selected_habit_id is None or not isinstance(date_str, str):
            return
        self._edit_day_comment(self._selected_habit_id, date_str)

    def _on_week_all_comments_requested(self, habit_id: int) -> None:
        self._on_habit_selected(habit_id)
        self._show_all_comments()

    def _on_week_day_comment_requested(self, habit_id: int, day_index: int) -> None:
        if day_index < 0 or day_index >= len(self._week_dates):
            return
        self._selected_habit_id = habit_id
        self._edit_day_comment(habit_id, self._week_dates[day_index].isoformat())

    def _on_week_day_toggled(self, habit_id: int, day_index: int) -> None:
        if self._db is None or day_index < 0 or day_index >= len(self._week_dates):
            return
        self._selected_habit_id = habit_id
        day = self._week_dates[day_index]
        self._toggle_date(habit_id, day.isoformat())

    def _on_week_day_value_set(self, habit_id: int, day_index: int, value: object) -> None:
        if self._db is None or day_index < 0 or day_index >= len(self._week_dates):
            return
        self._selected_habit_id = habit_id
        day = self._week_dates[day_index]
        self._set_date_value(habit_id, day.isoformat(), value)

    def _rebuild_habit_list(self) -> None:
        if self._db is None:
            return
        self._clear_habit_list()
        habits = self._habits()
        if not habits:
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
            stats = self._habit_stats(habit_id)
            habit_row = HabitRow()
            habit_row.set_habit_data(
                habit_id,
                name,
                stats.total_checkins,
                stats.streak,
                self._week_values_for(habit_id),
                selected=habit_id == self._selected_habit_id,
                emoji=emoji,
                allows_number=_habit_allows_number(row),
                week_comments=self._week_comments_for(habit_id),
                week_dates=self._week_dates,
            )
            habit_row.selected.connect(self._on_habit_selected)
            habit_row.edit_requested.connect(self._on_habit_edit_requested)
            habit_row.context_menu_requested.connect(self._on_habit_row_context_menu)
            habit_row.day_toggled.connect(self._on_week_day_toggled)
            habit_row.day_value_set.connect(self._on_week_day_value_set)
            habit_row.day_comment_requested.connect(self._on_week_day_comment_requested)
            habit_row.all_comments_requested.connect(self._on_week_all_comments_requested)
            self._habit_rows[habit_id] = habit_row
            self._list_layout.insertWidget(self._list_layout.count() - 1, habit_row)

    def _refresh_detail(self) -> None:
        if self._db is None or self._selected_habit_id is None:
            self._show_empty_detail()
            return

        habit = next((row for row in self._habits() if int(row[0]) == self._selected_habit_id), None)
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
        stats = self._habit_stats(habit_id)
        rate = round(100 * monthly / days_in_period) if days_in_period > 0 else 0

        self._stat_monthly.set_value(f"{monthly} Days")
        self._stat_total.set_value(f"{stats.total_checkins} Days")
        self._stat_rate.set_value(f"{rate}%")
        self._stat_streak.set_value(f"{stats.streak} Days")

        day_values = self._db.get_habit_values_between(habit_id, month_start, month_end)
        self._calendar.set_available_years(self._db.get_habit_years(habit_id))
        comment_dates = self._comment_index.get(habit_id, set())
        self._calendar.set_month(
            year,
            month,
            day_values,
            allows_number=_habit_allows_number(habit),
            today=today,
            comment_dates=comment_dates,
        )
        self._log_title.setText(f"Habit Log on {_month_name(month)}.")
        self._refresh_habit_log(habit_id, month_start, month_end, comment_dates)

    def _refresh_habit_log(
        self,
        habit_id: int | None,
        month_start: str,
        month_end: str,
        comment_dates: set[str],
    ) -> None:
        self._log_list.clear()
        if habit_id is None:
            self._log_placeholder.setText("No comments this month yet.")
            self._log_placeholder.show()
            self._log_list.hide()
            return
        month_dates = sorted(
            (day for day in comment_dates if month_start <= day <= month_end),
            reverse=True,
        )
        if not month_dates:
            self._log_placeholder.setText("No comments this month yet.")
            self._log_placeholder.show()
            self._log_list.hide()
            return
        self._log_placeholder.hide()
        self._log_list.show()
        for date_str in month_dates:
            text = self._comments.comment(habit_id, date_str)
            row = QListWidgetItem(f"{date_str}  {preview_habit_comment(text)}")
            row.setData(Qt.ItemDataRole.UserRole, date_str)
            self._log_list.addItem(row)

    def _reload_comment_index(self) -> None:
        if self._db is None or not self._comments.is_configured():
            self._comment_index = {}
            return
        habit_ids = [int(row[0]) for row in self._habits()]
        self._comment_index = self._comments.dates_with_comments(habit_ids)

    def _set_date_value(self, habit_id: int, date_str: str, value: object) -> None:
        if self._db is None or _is_future_date(date_str):
            return
        if value is not None and not isinstance(value, int):
            return
        stored = None if value is None else int(value)
        ok = self._db.set_habit_checkin(habit_id, date_str, stored)
        if not ok:
            QMessageBox.warning(self, "Database Error", "Failed to set check-in.")
            return
        self._after_checkin_changed(habit_id, sound_value=stored)

    def _set_empty_state_visible(self, *, visible: bool) -> None:
        """Show the Add habit call-to-action instead of the habit list.

        Args:

        - `visible` (`bool`): When `True`, show the empty-state button page.

        """
        stack = getattr(self, "_stack", None)
        empty = getattr(self, "_empty_state", None)
        if stack is None or empty is None:
            return
        stack.setCurrentWidget(empty if visible else stack.widget(0))

    def _show_all_comments(self) -> None:
        if self._selected_habit_id is None:
            return
        if not self._comments.is_configured():
            QMessageBox.warning(
                self,
                "Comments",
                "Habit comments folder is not configured. Set path_notes or path_habit_comments in config.json.",
            )
            return
        habit_id = self._selected_habit_id
        name = self._habit_display_name(habit_id)
        dialog = HabitCommentsListDialog(self, habit_name=name, comments=self._comments.comments_for_habit(habit_id))
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        date_str = dialog.chosen_date()
        if date_str:
            self._edit_day_comment(habit_id, date_str)

    def _show_empty_detail(self) -> None:
        self._detail_name.setText("Select a habit")
        self._stat_monthly.set_value("-")
        self._stat_total.set_value("-")
        self._stat_rate.set_value("-")
        self._stat_streak.set_value("-")
        today = _local_today()
        self._calendar.set_available_years([])
        self._calendar.set_month(today.year, today.month, {}, today=today)
        self._log_title.setText(f"Habit Log on {_month_name(today.month)}.")
        self._refresh_habit_log(None, "", "", set())

    def _toggle_date(self, habit_id: int, date_str: str) -> None:
        if self._db is None or _is_future_date(date_str):
            return
        ok = self._db.toggle_habit_checkin(habit_id, date_str)
        if not ok:
            QMessageBox.warning(self, "Database Error", "Failed to toggle check-in.")
            return
        stored = self._db.get_habit_values_between(habit_id, date_str, date_str)
        self._after_checkin_changed(habit_id, sound_value=stored.get(date_str))

    def _update_habit_row(self, habit_id: int) -> None:
        """Refresh one list row without destroying the widget tree."""
        row = self._habit_rows.get(habit_id)
        if row is None:
            return
        habits_by_id = {int(item[0]): item for item in self._habits()}
        habit = habits_by_id.get(habit_id)
        if habit is None:
            return
        name = str(habit[_NAME_COLUMN] or f"Habit {habit_id}")
        emoji = normalize_habit_emoji(
            str(habit[_EMOJI_COLUMN]) if len(habit) > _EMOJI_COLUMN else "",
            habit_id=habit_id,
        )
        stats = self._habit_stats(habit_id)
        row.set_habit_data(
            habit_id,
            name,
            stats.total_checkins,
            stats.streak,
            self._week_values_for(habit_id),
            selected=habit_id == self._selected_habit_id,
            emoji=emoji,
            allows_number=_habit_allows_number(habit),
            week_comments=self._week_comments_for(habit_id),
            week_dates=self._week_dates,
        )

    # --- Data refresh ----------------------------------------------------

    def _update_week_bar(self) -> None:
        if self._db is None:
            return
        today = _local_today()
        habit_ids = [int(row[0]) for row in self._habits()]
        total = len(habit_ids)
        week_values = self._week_values_map()
        for i, day in enumerate(self._week_dates):
            caption = f"{weekday_short(day.weekday())} {day.day}"
            if total == 0:
                ratio = 0.0
            else:
                date_str = day.isoformat()
                done = sum(1 for hid in habit_ids if (week_values.get(hid, {}).get(date_str) or 0) > 0)
                ratio = done / total
            self._week_headers[i].set_day(caption, ratio, is_today=day == today)

    def _week_comments_for(self, habit_id: int) -> list[bool]:
        """Return whether each visible week day has a comment."""
        dates = self._comment_index.get(habit_id, set())
        return [day.isoformat() in dates for day in self._week_dates]

    def _week_values_for(self, habit_id: int) -> list[int | None]:
        """Return stored values for the visible week, or ``None`` when no record exists."""
        if self._db is None or not self._week_dates:
            return [None] * 7
        stored = self._week_values_map().get(habit_id, {})
        return [stored.get(day.isoformat()) for day in self._week_dates]

    def _week_values_map(self) -> dict[int, dict[str, int]]:
        """Return week values for all habits, loading them once per refresh."""
        if self._week_values_cache is None:
            if self._db is None or not self._week_dates:
                self._week_values_cache = {}
            else:
                self._week_values_cache = self._db.get_habit_values_between_map(
                    [int(row[0]) for row in self._habits()],
                    self._week_dates[0].isoformat(),
                    self._week_dates[-1].isoformat(),
                )
        return self._week_values_cache
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None, *, app_config: dict[str, Any] | None = None) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None, *, app_config: dict[str, Any] | None = None) -> None:  # noqa: D107
        super().__init__(parent)
        self._db: DatabaseManager | None = None
        self._selected_habit_id: int | None = None
        today = _local_today()
        self._calendar_year = today.year
        self._calendar_month = today.month
        self._week_dates: list[date] = []
        self._habit_rows: dict[int, HabitRow] = {}
        self._app_config: dict[str, Any] = app_config if app_config is not None else {}
        self._comments = HabitCommentsStore.from_config(self._app_config)
        self._comment_index: dict[int, set[str]] = {}
        # Per-refresh caches: without them one refresh costs ~10 queries per habit.
        self._habits_cache: list[list[Any]] | None = None
        self._stats_cache: dict[int, HabitStats] | None = None
        self._week_values_cache: dict[int, dict[str, int]] | None = None

        self.setAutoFillBackground(True)
        self.setStyleSheet("HabitDashboardWidget { background: #FFFFFF; }")
        self._build_ui()
        preload_habit_checkin_sounds()
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
        self._invalidate_caches()
        if self._db is None:
            self._comment_index = {}
            self._clear_habit_list()
            self._show_empty_detail()
            self._set_empty_state_visible(visible=True)
            return

        habits = self._habits()
        if not habits:
            self._week_dates = _last_seven_days(_local_today())
            self._comment_index = {}
            self._clear_habit_list()
            self._selected_habit_id = None
            self._show_empty_detail()
            self._set_empty_state_visible(visible=True)
            return

        self._set_empty_state_visible(visible=False)
        self._week_dates = _last_seven_days(_local_today())
        self._reload_comment_index()
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
