---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `presentation_mode.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_presentation_window_title`](#-function-apply_presentation_window_title)
- [🔧 Function `create_presentation_database`](#-function-create_presentation_database)
- [🔧 Function `install_presentation_mode_action`](#-function-install_presentation_mode_action)
- [🔧 Function `presentation_ticktick_db_path`](#-function-presentation_ticktick_db_path)
- [🔧 Function `strip_presentation_title_suffix`](#-function-strip_presentation_title_suffix)
- [🔧 Function `sync_presentation_mode_action`](#-function-sync_presentation_mode_action)

</details>

## 🔧 Function `apply_presentation_window_title`

```python
def apply_presentation_window_title(window: QWidget, *, enabled: bool) -> None
```

Set or clear the presentation-mode suffix on the window title and caption.

<details>
<summary>Code:</summary>

```python
def apply_presentation_window_title(window: QWidget, *, enabled: bool) -> None:
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
```

</details>

## 🔧 Function `create_presentation_database`

```python
def create_presentation_database(app: PresentationApp) -> Path
```

Create a temp SQLite DB from `recover.sql` plus synthetic rows including today.

Args:

- `app` (`PresentationApp`): Tracker app ID.

Returns:

- `Path`: Path to the new `{app}.db` under a temp folder.

Raises:

- `FileNotFoundError`: When `recover.sql` is missing.
- `RuntimeError`: When the database file cannot be created.

<details>
<summary>Code:</summary>

```python
def create_presentation_database(app: PresentationApp) -> Path:
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
```

</details>

## 🔧 Function `install_presentation_mode_action`

```python
def install_presentation_mode_action(window: QWidget, menu: QMenu | None, *, get_enabled: Callable[[], bool], set_enabled: Callable[..., None]) -> QAction | None
```

Add a checkable Commands → Presentation mode action.

Args:

- `window` (`QWidget`): Host window (parent of the action).
- [`menu`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-menu) (`QMenu | None`): Commands menu; no-op when missing.
- `get_enabled` (`Callable[[], bool]`): Current presentation flag.
- [`set_enabled`](../../spellcheck/highlighter.g.md#%EF%B8%8F-method-set_enabled) (`Callable[..., None]`): Apply the new flag (`enabled=`).

Returns:

- `QAction | None`: Created action, or `None` when [`menu`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-menu) is missing.

<details>
<summary>Code:</summary>

```python
def install_presentation_mode_action(
    window: QWidget,
    menu: QMenu | None,
    *,
    get_enabled: Callable[[], bool],
    set_enabled: Callable[..., None],
) -> QAction | None:
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
```

</details>

## 🔧 Function `presentation_ticktick_db_path`

```python
def presentation_ticktick_db_path(habits_db_path: Path) -> Path
```

Return the synthetic TickTick DB next to a habits presentation database.

<details>
<summary>Code:</summary>

```python
def presentation_ticktick_db_path(habits_db_path: Path) -> Path:
    return habits_db_path.parent / "TickTick.db"
```

</details>

## 🔧 Function `strip_presentation_title_suffix`

```python
def strip_presentation_title_suffix(title: str) -> str
```

Return `title` without the presentation-mode suffix.

<details>
<summary>Code:</summary>

```python
def strip_presentation_title_suffix(title: str) -> str:
    text = title.strip()
    if text.endswith(PRESENTATION_TITLE_SUFFIX):
        return text[: -len(PRESENTATION_TITLE_SUFFIX)].rstrip()
    return text
```

</details>

## 🔧 Function `sync_presentation_mode_action`

```python
def sync_presentation_mode_action(window: Any) -> None
```

Update the check state of a previously installed presentation action.

<details>
<summary>Code:</summary>

```python
def sync_presentation_mode_action(window: Any) -> None:
    action = getattr(window, "_presentation_mode_action", None)
    if not isinstance(action, QAction):
        return
    enabled = bool(getattr(window, "presentation_mode", False))
    action.blockSignals(True)  # noqa: FBT003
    action.setChecked(enabled)
    action.blockSignals(False)  # noqa: FBT003
```

</details>
