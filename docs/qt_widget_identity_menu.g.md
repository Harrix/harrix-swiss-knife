---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_widget_identity_menu.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `WidgetIdentityEventFilter`](#%EF%B8%8F-class-widgetidentityeventfilter)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
- [🔧 Function `add_widget_identity_actions`](#-function-add_widget_identity_actions)
- [🔧 Function `ensure_widget_object_name`](#-function-ensure_widget_object_name)
- [🔧 Function `format_copy_class_name_menu_label`](#-function-format_copy_class_name_menu_label)
- [🔧 Function `format_copy_object_name_menu_label`](#-function-format_copy_object_name_menu_label)
- [🔧 Function `format_copy_text_menu_label`](#-function-format_copy_text_menu_label)
- [🔧 Function `install_widget_identity_context_menus`](#-function-install_widget_identity_context_menus)
- [🔧 Function `resolve_identity_widget`](#-function-resolve_identity_widget)
- [🔧 Function `show_widget_identity_context_menu`](#-function-show_widget_identity_context_menu)
- [🔧 Function `truncate_text_preview`](#-function-truncate_text_preview)
- [🔧 Function `widget_class_name_for_copy`](#-function-widget_class_name_for_copy)
- [🔧 Function `widget_object_name_for_copy`](#-function-widget_object_name_for_copy)
- [🔧 Function `widget_text_for_copy`](#-function-widget_text_for_copy)

</details>

## 🏛️ Class `WidgetIdentityEventFilter`

```python
class WidgetIdentityEventFilter(QObject)
```

Application filter: auto object names + middle-click identity menu.

<details>
<summary>Code:</summary>

```python
class WidgetIdentityEventFilter(QObject):

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        """Assign missing object names; open the identity menu on middle-click."""
        if event.type() in {QEvent.Type.Polish, QEvent.Type.Show} and isinstance(obj, QWidget):
            ensure_widget_object_name(obj)
            return False
        if event.type() != QEvent.Type.MouseButtonPress or not isinstance(event, QMouseEvent):
            return False
        if event.button() != Qt.MouseButton.MiddleButton:
            return False
        widget = resolve_identity_widget(obj)
        if widget is None or _is_menu_chrome(widget) or _owns_middle_click_menu(widget):
            return False
        show_widget_identity_context_menu(widget, event.globalPosition().toPoint())
        return True
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool
```

Assign missing object names; open the identity menu on middle-click.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() in {QEvent.Type.Polish, QEvent.Type.Show} and isinstance(obj, QWidget):
            ensure_widget_object_name(obj)
            return False
        if event.type() != QEvent.Type.MouseButtonPress or not isinstance(event, QMouseEvent):
            return False
        if event.button() != Qt.MouseButton.MiddleButton:
            return False
        widget = resolve_identity_widget(obj)
        if widget is None or _is_menu_chrome(widget) or _owns_middle_click_menu(widget):
            return False
        show_widget_identity_context_menu(widget, event.globalPosition().toPoint())
        return True
```

</details>

## 🔧 Function `add_widget_identity_actions`

```python
def add_widget_identity_actions(menu: QMenu, widget: QWidget) -> None
```

Append Copy object name / Copy class name / Copy text actions for `widget`.

<details>
<summary>Code:</summary>

```python
def add_widget_identity_actions(menu: QMenu, widget: QWidget) -> None:
    object_name = widget_object_name_for_copy(widget)
    class_name = widget_class_name_for_copy(widget)
    copy_name = menu.addAction(format_copy_object_name_menu_label(object_name))
    copy_name.triggered.connect(lambda *_args, text=object_name: _copy_text(text))
    copy_class = menu.addAction(format_copy_class_name_menu_label(class_name))
    copy_class.triggered.connect(lambda *_args, text=class_name: _copy_text(text))
    widget_text = widget_text_for_copy(widget)
    if widget_text is not None:
        copy_value = menu.addAction(format_copy_text_menu_label(widget_text))
        copy_value.triggered.connect(lambda *_args, text=widget_text: _copy_text(text))
```

</details>

## 🔧 Function `ensure_widget_object_name`

```python
def ensure_widget_object_name(widget: QWidget) -> str
```

Set a stable object name when missing; return the name used for copy.

<details>
<summary>Code:</summary>

```python
def ensure_widget_object_name(widget: QWidget) -> str:
    existing = widget.objectName().strip()
    if existing:
        return existing
    if _is_menu_chrome(widget):
        return type(widget).__name__
    name = _allocate_object_name(_compose_object_name_base(widget))
    widget.setObjectName(name)
    return name
```

</details>

## 🔧 Function `format_copy_class_name_menu_label`

```python
def format_copy_class_name_menu_label(class_name: str) -> str
```

Build the Copy class name menu label.

<details>
<summary>Code:</summary>

```python
def format_copy_class_name_menu_label(class_name: str) -> str:
    return f"{_COPY_CLASS_NAME_PREFIX}{class_name})"
```

</details>

## 🔧 Function `format_copy_object_name_menu_label`

```python
def format_copy_object_name_menu_label(object_name: str) -> str
```

Build the Copy object name menu label.

<details>
<summary>Code:</summary>

```python
def format_copy_object_name_menu_label(object_name: str) -> str:
    return f"{_COPY_OBJECT_NAME_PREFIX}{object_name})"
```

</details>

## 🔧 Function `format_copy_text_menu_label`

```python
def format_copy_text_menu_label(text: str, max_len: int = _COPY_TEXT_PREVIEW_MAX_LEN) -> str
```

Build the Copy text menu label with a single-line truncated preview.

<details>
<summary>Code:</summary>

```python
def format_copy_text_menu_label(text: str, max_len: int = _COPY_TEXT_PREVIEW_MAX_LEN) -> str:
    return f"{_COPY_TEXT_PREFIX}{truncate_text_preview(text, max_len=max_len)}"
```

</details>

## 🔧 Function `install_widget_identity_context_menus`

```python
def install_widget_identity_context_menus(app: QApplication) -> None
```

Install an app-wide filter for auto object names and the identity menu.

<details>
<summary>Code:</summary>

```python
def install_widget_identity_context_menus(app: QApplication) -> None:
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP_FILTER)
    if isinstance(existing, WidgetIdentityEventFilter):
        return
    event_filter = WidgetIdentityEventFilter(app)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP_FILTER, event_filter)
```

</details>

## 🔧 Function `resolve_identity_widget`

```python
def resolve_identity_widget(obj: QObject | None) -> QWidget | None
```

Map a click target (often a viewport) to the identity widget.

<details>
<summary>Code:</summary>

```python
def resolve_identity_widget(obj: QObject | None) -> QWidget | None:
    if not isinstance(obj, QWidget):
        return None
    widget: QWidget = obj
    parent = widget.parentWidget()
    if parent is not None:
        viewport = getattr(parent, "viewport", None)
        if callable(viewport) and viewport() is widget:
            return parent
    return widget
```

</details>

## 🔧 Function `show_widget_identity_context_menu`

```python
def show_widget_identity_context_menu(widget: QWidget, global_pos: QPoint) -> None
```

Show Copy object name / Copy class name / Copy text for `widget` at `global_pos`.

<details>
<summary>Code:</summary>

```python
def show_widget_identity_context_menu(widget: QWidget, global_pos: QPoint) -> None:
    menu = FluentMenu("", widget)
    add_widget_identity_actions(menu, widget)
    apply_leading_chrome_icons(menu)
    menu.refresh_theme()
    menu.exec(global_pos)
```

</details>

## 🔧 Function `truncate_text_preview`

```python
def truncate_text_preview(text: str, max_len: int = _COPY_TEXT_PREVIEW_MAX_LEN) -> str
```

Return a single-line preview, ending with `…` when longer than `max_len`.

<details>
<summary>Code:</summary>

```python
def truncate_text_preview(text: str, max_len: int = _COPY_TEXT_PREVIEW_MAX_LEN) -> str:
    preview = _WHITESPACE_RE.sub(" ", text.strip())
    if max_len <= 0:
        return _ELLIPSIS
    if len(preview) <= max_len:
        return preview
    return preview[:max_len].rstrip() + _ELLIPSIS
```

</details>

## 🔧 Function `widget_class_name_for_copy`

```python
def widget_class_name_for_copy(widget: QWidget) -> str
```

Return the class name shown and copied for `widget`.

<details>
<summary>Code:</summary>

```python
def widget_class_name_for_copy(widget: QWidget) -> str:
    return type(widget).__qualname__
```

</details>

## 🔧 Function `widget_object_name_for_copy`

```python
def widget_object_name_for_copy(widget: QWidget) -> str
```

Return the object name shown and copied for `widget`.

<details>
<summary>Code:</summary>

```python
def widget_object_name_for_copy(widget: QWidget) -> str:
    return ensure_widget_object_name(widget)
```

</details>

## 🔧 Function `widget_text_for_copy`

```python
def widget_text_for_copy(widget: QWidget) -> str | None
```

Return visible text content for `widget`, or `None` when there is none.

Reads `toPlainText` / `currentText` / `text` (labels, edits, buttons, combos,
spin boxes). Group titles are included; placeholders and tooltips are not.

<details>
<summary>Code:</summary>

```python
def widget_text_for_copy(widget: QWidget) -> str | None:
    for attr in _TEXT_GETTERS:
        getter = getattr(widget, attr, None)
        if not callable(getter):
            continue
        try:
            value = getter()
        except TypeError:
            continue
        if isinstance(value, str) and value.strip():
            return value
    title = getattr(widget, "title", None)
    if callable(title):
        try:
            value = title()
        except TypeError:
            value = None
        if isinstance(value, str) and value.strip():
            return value
    return None
```

</details>
