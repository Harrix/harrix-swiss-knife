---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainWindow`](#%EF%B8%8F-class-mainwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🔧 Function `main`](#-function-main)

</details>

## 🏛️ Class `MainWindow`

```python
class MainWindow(AppWindowMixin, QMainWindow, Ui_MainWindow)
```

Track official Beat Saber clears across PC and Quest.

<details>
<summary>Code:</summary>

```python
class MainWindow(AppWindowMixin, QMainWindow, Ui_MainWindow):

    about_app_name = "Beat Saber tracker"
    about_description = "Compare PC/Quest ranks, find missing difficulties, and backup local saves."
    settings_app_id = "beat_saber"

    def __init__(self, *, hide_on_close: bool = False, presentation_mode: bool = False) -> None:
        """Build the window, open SQLite, and seed from backups when empty."""
        super().__init__()
        self.presentation_mode = presentation_mode
        self._apply_fluent_window_chrome()
        self.setupUi(self)
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self.db_manager: database_manager.DatabaseManager | None = None
        self._setup_ui()
        self._finish_fluent_window_chrome()
        apply_window_icon(self)
        self._init_hide_on_close(hide_on_close=hide_on_close)
        self._init_database()
        self._maybe_seed_from_backups()
        self._refresh_all_views()

    def _fill_table(self, table: Any, headers: list[str], rows: list[tuple[Any, ...]]) -> None:
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, value in enumerate(row):
                table.setItem(r, c, QTableWidgetItem(str(value)))

    def _init_database(self) -> None:
        """Open `sqlite_beat_saber` (create from `recover.sql` when missing)."""
        app_dir = Path(__file__).parent
        configured = Path(str(self._app_config.get("sqlite_beat_saber") or ""))
        if not str(configured):
            local = self._app_config.get("sqlite_habits")
            configured = (
                Path(str(local)).with_name("beat_saber.db")
                if local
                else Path.home() / "Dropbox" / "Databases" / "beat_saber.db"
            )

        with contextlib.suppress(Exception):
            QtSqliteDatabaseManagerBase.resolve_db_path_with_fallback(configured, "beat_saber")

        self.db_manager = init_tracker_database(
            self,
            configured,
            "beat_saber",
            app_dir / "recover.sql",
            database_manager.DatabaseManager,
            has_required_tables=lambda dm: dm.table_exists("songs") and dm.table_exists("clears_current"),
            missing_table_label="songs/clears_current",
        )

    def _maybe_seed_from_backups(self) -> None:
        """On empty DB, load catalog and ingest BeatSaber backup ZIPs."""
        if self.db_manager is None or self.presentation_mode:
            return
        if not self.db_manager.needs_first_run_seed():
            return
        seed = seed_official_catalog(self.db_manager.db_path)
        folder = beat_saber_backup_root(self._app_config)
        imported = ingest_backup_folder(self.db_manager.db_path, folder, seed_catalog=False)
        message_box.information(
            self,
            "Beat Saber tracker",
            f"{seed.message}\n{imported.message}\n\n" + "\n".join(imported.lines[:12]),
        )

    def _on_backup_db(self) -> None:
        if self.db_manager is None:
            return
        stamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S")
        dest_dir = beat_saber_backup_root(self._app_config) / "db" / f"beat-saber-db-{stamp}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / "beat_saber.db"
        shutil.copy2(self.db_manager.db_path, dest)
        message_box.information(self, "Backup DB", f"Copied database to:\n{dest}")

    def _on_export(self, source: str) -> None:
        if self.db_manager is None:
            return
        zip_path = default_export_zip_path(self._app_config)
        if source == "pc":
            result = export_pc_saves(zip_path)
        else:
            device = self._pick_quest_device()
            if device is None:
                return
            adb, serial = device
            result = export_quest_saves(adb, serial, zip_path)
        if result.ok and result.zip_path is not None:
            ingest_backup_zip(self.db_manager.db_path, result.zip_path, source_override=source)
        text = result.message
        if result.lines:
            text += "\n\n" + "\n".join(result.lines[-40:])
        message_box.information(self, f"Export {source.upper()}", text)
        self._refresh_all_views()

    def _on_import_backups(self) -> None:
        if self.db_manager is None:
            return
        folder = beat_saber_backup_root(self._app_config)
        choice = message_box.question(
            self,
            "Import backups",
            f"Import all `beat-saber-*.zip` from:\n{folder}\n\nYes = folder, No = pick ZIP files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if choice == QMessageBox.StandardButton.Yes:
            result = ingest_backup_folder(self.db_manager.db_path, folder)
            message_box.information(self, "Import backups", result.message + "\n\n" + "\n".join(result.lines[:20]))
            self._refresh_all_views()
            return
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Beat Saber backup ZIPs",
            str(folder),
            "ZIP archives (*.zip)",
        )
        if not files:
            return
        lines: list[str] = []
        for file_path in files:
            one = ingest_backup_zip(self.db_manager.db_path, file_path)
            lines.append(f"{Path(file_path).name}: {one.message}")
        message_box.information(self, "Import backups", "\n".join(lines))
        self._refresh_all_views()

    def _on_import_save(self, source: str) -> None:
        if self.db_manager is None:
            return
        folder = beat_saber_backup_root(self._app_config)
        chosen, _ = QFileDialog.getOpenFileName(self, f"Import ZIP to {source.upper()}", str(folder), "ZIP (*.zip)")
        if not chosen:
            return
        zip_path = Path(chosen)
        proceed = message_box.question(
            self,
            f"Import {source.upper()}",
            f"Overwrite Beat Saber saves on {source.upper()} with `{zip_path.name}`?\nQuit Beat Saber first.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if proceed != QMessageBox.StandardButton.Yes:
            return
        if source == "pc":
            result = import_pc_saves(zip_path)
        else:
            device = self._pick_quest_device()
            if device is None:
                return
            adb, serial = device
            result = import_quest_saves(adb, serial, zip_path)
        if result.ok:
            ingest_backup_zip(self.db_manager.db_path, zip_path, source_override=source)
        message_box.information(self, f"Import {source.upper()}", result.message)
        self._refresh_all_views()

    def _on_refresh_catalog(self) -> None:
        if self.db_manager is None:
            return
        result = seed_official_catalog(self.db_manager.db_path)
        message_box.information(self, "Refresh catalog", result.message)
        self._refresh_all_views()

    def _on_sync_pc(self) -> None:
        if self.db_manager is None:
            return
        player = pc_saves_dir() / "PlayerData.dat"
        if not player.is_file():
            message_box.warning(self, "Sync from PC", f"`PlayerData.dat` not found:\n{player}")
            return
        result = ingest_player_data(self.db_manager.db_path, player, source="pc", note="sync from PC")
        message_box.information(self, "Sync from PC", result.message)
        self._refresh_all_views()

    def _on_sync_quest(self) -> None:
        if self.db_manager is None:
            return
        device = self._pick_quest_device()
        if device is None:
            return
        adb, serial = device
        remote = f"{quest_remote_files_dir()}/PlayerData.dat"
        with tempfile.TemporaryDirectory(prefix="hsk-bs-sync-") as tmp:
            local = Path(tmp) / "PlayerData.dat"
            process = adb_pull(adb, serial, remote, local)
            if process.returncode != 0 or not local.is_file():
                detail = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
                message_box.warning(self, "Sync from Quest", f"adb pull failed.\n{detail}")
                return
            result = ingest_player_data(
                self.db_manager.db_path,
                local,
                source="quest",
                note=f"sync from Quest {serial}",
            )
        message_box.information(self, "Sync from Quest", result.message)
        self._refresh_all_views()

    def _pick_quest_device(self) -> tuple[Path, str] | None:
        adb = resolve_adb()
        if adb is None:
            message_box.warning(self, "Quest", f"adb not found. {ANDROID_SDK_SETUP_HINT}")
            return None
        authorized, unauthorized, output = list_adb_device_states(adb)
        if unauthorized and not authorized:
            message_box.warning(self, "Quest", "Headset unauthorized — allow USB debugging on Quest.")
            return None
        if not authorized:
            message_box.warning(self, "Quest", "No authorized adb devices.\n" + (output or ""))
            return None
        if len(authorized) == 1:
            return adb, authorized[0]
        # Prefer first authorized device for simplicity in the app.
        return adb, authorized[0]

    def _refresh_all_views(self) -> None:
        """Reload summary and the active tab table."""
        if self.db_manager is None:
            return
        stats = self.db_manager.summary_stats()
        self.label_summary.setText(
            f"Official songs: {stats.official_songs} | "
            f"PC clears: {stats.clears_pc} (FC {stats.fc_pc}) | "
            f"Quest clears: {stats.clears_quest} (FC {stats.fc_quest}) | "
            f"Missing Standard (best): {stats.missing_standard} | "
            f"Sync runs: {stats.sync_runs}"
        )
        source = self._selected_source()
        difficulty = self._selected_difficulty()
        require_fc = self.check_require_fc.isChecked()
        search = self.line_search.text()
        tab = self.tabWidget.currentWidget()
        if tab is self.tab_missing:
            self._fill_table(
                self.table_missing,
                ["Song", "Pack", "Difficulty", "Status", "level_id"],
                self.db_manager.list_missing(
                    source=source,
                    difficulty=difficulty,
                    require_fc=require_fc,
                    search=search,
                ),
            )
        elif tab is self.tab_compare:
            self._fill_table(
                self.table_compare,
                ["Song", "Pack", "Diff", "PC", "PC FC", "Quest", "Quest FC", "Verdict"],
                self.db_manager.list_compare(difficulty=difficulty, search=search),
            )
        elif tab is self.tab_clears:
            self._fill_table(
                self.table_clears,
                ["Song", "Pack", "Source", "Mode", "Diff", "Rank", "FC", "Score", "Plays", "Observed"],
                self.db_manager.list_clears(source=source if source in {"pc", "quest"} else "best", search=search),
            )
        else:
            self._fill_table(
                self.table_history,
                ["Observed", "Song", "Pack", "Source", "Mode", "Diff", "Rank", "FC", "Score"],
                self.db_manager.list_history(search=search),
            )

    def _selected_difficulty(self) -> int | None:
        index = self.combo_difficulty.currentIndex()
        if index <= 0:
            return None
        return index - 1

    def _selected_source(self) -> str:
        text = self.combo_source.currentText().casefold()
        if text == "pc":
            return "pc"
        if text == "quest":
            return "quest"
        return "best"

    def _setup_ui(self) -> None:
        """Wire menus, filters, and table headers."""
        self.action_sync_pc.triggered.connect(self._on_sync_pc)
        self.action_sync_quest.triggered.connect(self._on_sync_quest)
        self.action_import_backups.triggered.connect(self._on_import_backups)
        self.action_refresh_catalog.triggered.connect(self._on_refresh_catalog)
        self.action_refresh_views.triggered.connect(self._refresh_all_views)
        self.action_export_pc.triggered.connect(lambda: self._on_export("pc"))
        self.action_export_quest.triggered.connect(lambda: self._on_export("quest"))
        self.action_import_pc.triggered.connect(lambda: self._on_import_save("pc"))
        self.action_import_quest.triggered.connect(lambda: self._on_import_save("quest"))
        self.action_backup_db.triggered.connect(self._on_backup_db)

        self.combo_source.currentIndexChanged.connect(self._refresh_all_views)
        self.combo_difficulty.currentIndexChanged.connect(self._refresh_all_views)
        self.check_require_fc.stateChanged.connect(self._refresh_all_views)
        self.line_search.textChanged.connect(self._refresh_all_views)
        self.tabWidget.currentChanged.connect(self._refresh_all_views)

        for table in (self.table_missing, self.table_compare, self.table_clears, self.table_history):
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(table.SelectionBehavior.SelectRows)
            table.setEditTriggers(table.EditTrigger.NoEditTriggers)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)

        self.toolBar.setStyleSheet(button_idle_qss())
        self._setup_window_size_and_position()
        self._connect_exit_about_actions()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, hide_on_close: bool = False, presentation_mode: bool = False) -> None
```

Build the window, open SQLite, and seed from backups when empty.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, hide_on_close: bool = False, presentation_mode: bool = False) -> None:
        super().__init__()
        self.presentation_mode = presentation_mode
        self._apply_fluent_window_chrome()
        self.setupUi(self)
        self._app_config: dict[str, Any] = h.dev.config_load(get_config_path_str())
        self.db_manager: database_manager.DatabaseManager | None = None
        self._setup_ui()
        self._finish_fluent_window_chrome()
        apply_window_icon(self)
        self._init_hide_on_close(hide_on_close=hide_on_close)
        self._init_database()
        self._maybe_seed_from_backups()
        self._refresh_all_views()
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

Run the Beat Saber tracker as a standalone app.

<details>
<summary>Code:</summary>

```python
def main() -> None:
    run_app_main(MainWindow)
```

</details>
