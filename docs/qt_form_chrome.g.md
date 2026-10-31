---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_form_chrome.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `apply_form_chrome`](#-function-apply_form_chrome)
- [🔧 Function `install_form_chrome`](#-function-install_form_chrome)

</details>

## 🔧 Function `apply_form_chrome`

```python
def apply_form_chrome(root: QWidget) -> None
```

Apply Lucide toggles and dialog surfaces to [`root`](apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) and its children now.

<details>
<summary>Code:</summary>

```python
def apply_form_chrome(root: QWidget) -> None:
    _apply_widget_chrome(root)
    for widget in root.findChildren(QWidget):
        if isinstance(widget, (QCheckBox, QRadioButton)):
            _apply_widget_chrome(widget)
```

</details>

## 🔧 Function `install_form_chrome`

```python
def install_form_chrome(app: QApplication) -> None
```

Install the shared form chrome polish filter once on `app`.

<details>
<summary>Code:</summary>

```python
def install_form_chrome(app: QApplication) -> None:
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP)
    if isinstance(existing, _FormChromeFilter):
        return
    event_filter = _FormChromeFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP, event_filter)
```

</details>
