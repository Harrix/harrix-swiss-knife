---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `install.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SpellcheckEventFilter`](#%EF%B8%8F-class-spellcheckeventfilter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `eventFilter`](#%EF%B8%8F-method-eventfilter)
- [🔧 Function `attach_to_widget`](#-function-attach_to_widget)
- [🔧 Function `install_spellcheck`](#-function-install_spellcheck)
- [🔧 Function `scan_and_attach`](#-function-scan_and_attach)
- [🔧 Function `should_attach_spellcheck`](#-function-should_attach_spellcheck)
- [🔧 Function `widget_is_inside_item_view`](#-function-widget_is_inside_item_view)

</details>

## 🏛️ Class `SpellcheckEventFilter`

```python
class SpellcheckEventFilter(QObject)
```

Attach spellcheck when text widgets appear or receive focus.

<details>
<summary>Code:</summary>

```python
class SpellcheckEventFilter(QObject):

    def __init__(self, app: QApplication, engine: SpellEngine | None = None) -> None:
        """Create the filter; `engine` defaults to the process-wide singleton."""
        super().__init__(app)
        self._engine = engine if engine is not None else get_spell_engine()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Attach on show/focus for eligible editors."""
        if event.type() == QEvent.Type.ChildAdded and isinstance(event, QChildEvent):
            child = event.child()
            if isinstance(child, QWidget) and is_text_editor(child):
                attach_to_widget(child, self._engine)
            return False
        if event.type() not in (QEvent.Type.Show, QEvent.Type.FocusIn):
            return False
        if isinstance(watched, QWidget) and is_text_editor(watched):
            attach_to_widget(watched, self._engine)
        return False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, app: QApplication, engine: SpellEngine | None = None) -> None
```

Create the filter; `engine` defaults to the process-wide singleton.

<details>
<summary>Code:</summary>

```python
def __init__(self, app: QApplication, engine: SpellEngine | None = None) -> None:
        super().__init__(app)
        self._engine = engine if engine is not None else get_spell_engine()
```

</details>

### ⚙️ Method `eventFilter`

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```

Attach on show/focus for eligible editors.

<details>
<summary>Code:</summary>

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.Type.ChildAdded and isinstance(event, QChildEvent):
            child = event.child()
            if isinstance(child, QWidget) and is_text_editor(child):
                attach_to_widget(child, self._engine)
            return False
        if event.type() not in (QEvent.Type.Show, QEvent.Type.FocusIn):
            return False
        if isinstance(watched, QWidget) and is_text_editor(watched):
            attach_to_widget(watched, self._engine)
        return False
```

</details>

## 🔧 Function `attach_to_widget`

```python
def attach_to_widget(widget: QWidget, engine: SpellEngine | None = None) -> bool
```

Attach spellcheck UI to a supported editor. Returns `True` when attached.

<details>
<summary>Code:</summary>

```python
def attach_to_widget(widget: QWidget, engine: SpellEngine | None = None) -> bool:
    if not should_attach_spellcheck(widget):
        return False
    spell = engine if engine is not None else get_spell_engine()
    spell.ensure_loaded()
    widget.setProperty(_PROP_ATTACHED, "1")

    if isinstance(widget, QLineEdit):
        controller = LineEditSpellController(widget, spell)
        widget.setProperty(_PROP_CONTROLLER, controller)

        def _on_changed() -> None:
            controller.refresh()

        _install_context_hook(widget, spell, _on_changed)
        return True

    if isinstance(widget, (QPlainTextEdit, QTextEdit)):
        highlighter = SpellHighlighter(widget.document(), spell)
        widget.setProperty(_PROP_HIGHLIGHTER, highlighter)
        debounce = QTimer(widget)
        debounce.setSingleShot(True)
        debounce.setInterval(_DEBOUNCE_DOC_MS)

        def _rehighlight() -> None:
            highlighter.rehighlight_all()

        def _schedule_rehighlight() -> None:
            debounce.start()

        debounce.timeout.connect(_rehighlight)
        widget.textChanged.connect(_schedule_rehighlight)

        def _on_changed() -> None:
            highlighter.rehighlight_all()

        _install_context_hook(widget, spell, _on_changed)
        return True

    return False
```

</details>

## 🔧 Function `install_spellcheck`

```python
def install_spellcheck(app: QApplication, engine: SpellEngine | None = None) -> None
```

Install an application-wide filter that attaches spellcheck to text editors.

<details>
<summary>Code:</summary>

```python
def install_spellcheck(app: QApplication, engine: SpellEngine | None = None) -> None:
    if not isinstance(app, QApplication):
        return
    existing = app.property(_PROP_FILTER)
    if isinstance(existing, SpellcheckEventFilter):
        return
    spell = engine if engine is not None else get_spell_engine()
    QTimer.singleShot(0, spell.ensure_loaded)
    event_filter = SpellcheckEventFilter(app, spell)
    app.installEventFilter(event_filter)
    app.setProperty(_PROP_FILTER, event_filter)
    for widget in app.allWidgets():
        if is_text_editor(widget):
            attach_to_widget(widget, spell)
```

</details>

## 🔧 Function `scan_and_attach`

```python
def scan_and_attach(root: QWidget | None = None, engine: SpellEngine | None = None) -> int
```

Attach spellcheck under [`root`](../apps/habits/habit_comments.g.md#%EF%B8%8F-method-root) (or all app widgets). Returns attach count.

<details>
<summary>Code:</summary>

```python
def scan_and_attach(root: QWidget | None = None, engine: SpellEngine | None = None) -> int:
    spell = engine if engine is not None else get_spell_engine()
    count = 0
    if root is None:
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            return 0
        widgets: list[QWidget] = list(app.allWidgets())
    else:
        widgets = [root, *root.findChildren(QWidget)]
    for widget in widgets:
        if is_text_editor(widget) and attach_to_widget(widget, spell):
            count += 1
    return count
```

</details>

## 🔧 Function `should_attach_spellcheck`

```python
def should_attach_spellcheck(widget: QWidget) -> bool
```

Return whether global spellcheck should attach to `widget`.

<details>
<summary>Code:</summary>

```python
def should_attach_spellcheck(widget: QWidget) -> bool:
    if widget.property(_PROP_ATTACHED) == "1":
        return False
    if not is_text_editor(widget):
        return False
    if isinstance(widget, QTextBrowser):
        return False
    if widget_is_inside_item_view(widget):
        return False
    if isinstance(widget, QAbstractSpinBox):
        return False
    parent = widget.parent()
    if isinstance(parent, QAbstractSpinBox):
        return False
    if isinstance(widget, QLineEdit):
        echo = widget.echoMode()
        if echo in (QLineEdit.EchoMode.Password, QLineEdit.EchoMode.NoEcho):
            return False
        if widget.isReadOnly():
            return False
    elif isinstance(widget, (QPlainTextEdit, QTextEdit)) and widget.isReadOnly():
        return False
    return True
```

</details>

## 🔧 Function `widget_is_inside_item_view`

```python
def widget_is_inside_item_view(widget: QObject | None) -> bool
```

Return `True` when `widget` is under a `QAbstractItemView` (table/list editors).

<details>
<summary>Code:</summary>

```python
def widget_is_inside_item_view(widget: QObject | None) -> bool:
    current: QObject | None = widget
    while current is not None:
        if isinstance(current, QAbstractItemView):
            return True
        current = current.parent()
    return False
```

</details>
