---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `quick_tab_startup.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_open_quick_tab_preference`](#-function-apply_open_quick_tab_preference)
- [🔧 Function `install_open_quick_tab_checkbox`](#-function-install_open_quick_tab_checkbox)

</details>

## 🔧 Function `apply_open_quick_tab_preference`

```python
def apply_open_quick_tab_preference(tab_widget: QTabWidget, *, app: QuickTabAppName, config: dict[str, Any]) -> None
```

Select Quick or the second tab from the stored preference.

<details>
<summary>Code:</summary>

```python
def apply_open_quick_tab_preference(
    tab_widget: QTabWidget,
    *,
    app: QuickTabAppName,
    config: dict[str, Any],
) -> None:
    index = startup_tab_index(open_quick=get_open_quick_tab_on_startup(config, app))
    if 0 <= index < tab_widget.count():
        tab_widget.setCurrentIndex(index)
```

</details>

## 🔧 Function `install_open_quick_tab_checkbox`

```python
def install_open_quick_tab_checkbox(window: QWidget, *, app: QuickTabAppName, tab_layout: QVBoxLayout, tab_widget: QTabWidget) -> QCheckBox
```

Add the startup checkbox and select Quick or the second tab.

Args:

- `window` (`QWidget`): App main window; may expose `_app_config`.
- `app` (`QuickTabAppName`): `finance`, `food`, or `fitness`.
- `tab_layout` (`QVBoxLayout`): Layout of the first tab.
- `tab_widget` (`QTabWidget`): App tab widget.

Returns:

- `QCheckBox`: The installed preference checkbox.

<details>
<summary>Code:</summary>

```python
def install_open_quick_tab_checkbox(
    window: QWidget,
    *,
    app: QuickTabAppName,
    tab_layout: QVBoxLayout,
    tab_widget: QTabWidget,
) -> QCheckBox:
    config = _window_config(window)
    checkbox = QCheckBox("Open Quick tab on startup")
    checkbox.setObjectName(f"{app}OpenQuickTabOnStartup")
    checkbox.setChecked(get_open_quick_tab_on_startup(config, app))
    checkbox.setStyleSheet(_CHECKBOX_STYLE)
    checkbox.toggled.connect(lambda checked: _on_open_quick_tab_toggled(window, app, checked=checked))
    tab_layout.addWidget(checkbox)
    apply_open_quick_tab_preference(tab_widget, config=config, app=app)
    return checkbox
```

</details>
