---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_ui_effects.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `install_ui_effects`](#-function-install_ui_effects)
- [🔧 Function `suspended_polish_filters`](#-function-suspended_polish_filters)

</details>

## 🔧 Function `install_ui_effects`

```python
def install_ui_effects(app: QApplication) -> None
```

Disable combo popup slide animation and install shared form chrome.

On the `windows11` style the animated popup is painted once, then grabbed
and scrolled open, which reads as a blink every time a combo opens.

Also paints Lucide checkbox / radio indicators and white dialog surfaces.

Args:

- `app` (`QApplication`): Running application.

<details>
<summary>Code:</summary>

```python
def install_ui_effects(app: QApplication) -> None:
    app.setEffectEnabled(Qt.UIEffect.UI_AnimateCombo, enable=False)
    install_date_calendar_popups(app)
    install_form_chrome(app)
```

</details>

## 🔧 Function `suspended_polish_filters`

```python
def suspended_polish_filters(root: QWidget) -> Generator[None]
```

Detach the app-wide polish filters while [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) is restyled in bulk.

Every `setStyleSheet` on a container re-polishes its whole subtree, and each
event of each child goes through the Python application filters. Restyling a
tracker window that way costs seconds. The filters' work is replayed once on
[`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) afterwards.

Args:

- [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) (`QWidget`): Window or dialog that is about to be restyled.

<details>
<summary>Code:</summary>

```python
def suspended_polish_filters(root: QWidget) -> Generator[None]:
    global _suspend_depth  # noqa: PLW0603
    app = QApplication.instance()
    filters: list[QObject] = []
    if _suspend_depth == 0 and isinstance(app, QApplication):
        for prop in _POLISH_FILTER_PROPS:
            event_filter = app.property(prop)
            if isinstance(event_filter, QObject):
                app.removeEventFilter(event_filter)
                filters.append(event_filter)
    _suspend_depth += 1
    try:
        yield
    finally:
        _suspend_depth -= 1
        if isinstance(app, QApplication):
            for event_filter in filters:
                app.installEventFilter(event_filter)
        if filters:
            _replay_polish_filters(root)
```

</details>
