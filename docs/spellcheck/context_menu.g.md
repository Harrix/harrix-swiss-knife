---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `context_menu.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_dictionary_action`](#-function-add_dictionary_action)
- [🔧 Function `cursor_char_index`](#-function-cursor_char_index)
- [🔧 Function `editor_plain_text`](#-function-editor_plain_text)
- [🔧 Function `is_text_editor`](#-function-is_text_editor)
- [🔧 Function `misspelled_word_at`](#-function-misspelled_word_at)
- [🔧 Function `populate_spellcheck_menu`](#-function-populate_spellcheck_menu)
- [🔧 Function `popup_spellcheck_menu`](#-function-popup_spellcheck_menu)
- [🔧 Function `replace_word_span`](#-function-replace_word_span)

</details>

## 🔧 Function `add_dictionary_action`

```python
def add_dictionary_action(menu: QMenu, widget: TextEditor, *, engine: SpellEngine | None = None, global_pos: QPoint | None = None, on_added: Callable[[str], None] | None = None) -> QAction | None
```

Append **Add to dictionary** when a misspelled word is under the cursor.

Prefer [`populate_spellcheck_menu`](#-function-populate_spellcheck_menu) for the full context-menu UX.

<details>
<summary>Code:</summary>

```python
def add_dictionary_action(
    menu: QMenu,
    widget: TextEditor,
    *,
    engine: SpellEngine | None = None,
    global_pos: QPoint | None = None,
    on_added: Callable[[str], None] | None = None,
) -> QAction | None:
    spell = engine if engine is not None else get_spell_engine()
    span = misspelled_word_at(widget, spell, global_pos=global_pos)
    if span is None:
        return None
    _start, _end, word = span
    action = QAction(f'Add "{word}" to dictionary', menu)
    action.setObjectName("hskSpellcheckAddToDictionary")

    def _add() -> None:
        if spell.add_to_user_dictionary(word) and on_added is not None:
            on_added(word)

    action.triggered.connect(_add)
    menu.addAction(action)
    return action
```

</details>

## 🔧 Function `cursor_char_index`

```python
def cursor_char_index(widget: TextEditor, global_pos: QPoint | None = None) -> int
```

Return the character index under `global_pos` (or the caret if omitted).

<details>
<summary>Code:</summary>

```python
def cursor_char_index(widget: TextEditor, global_pos: QPoint | None = None) -> int:
    if isinstance(widget, QLineEdit):
        if global_pos is not None:
            local = widget.mapFromGlobal(global_pos)
            return widget.cursorPositionAt(local)
        return widget.cursorPosition()
    if global_pos is not None:
        local = widget.mapFromGlobal(global_pos)
        cursor = widget.cursorForPosition(local)
        return cursor.position()
    return widget.textCursor().position()
```

</details>

## 🔧 Function `editor_plain_text`

```python
def editor_plain_text(widget: TextEditor) -> str
```

Return the full plain text of a supported editor.

<details>
<summary>Code:</summary>

```python
def editor_plain_text(widget: TextEditor) -> str:
    if isinstance(widget, QLineEdit):
        return widget.text()
    return widget.toPlainText()
```

</details>

## 🔧 Function `is_text_editor`

```python
def is_text_editor(widget: QWidget) -> TypeGuard[TextEditor]
```

Return whether `widget` is a supported spellcheck editor type.

<details>
<summary>Code:</summary>

```python
def is_text_editor(widget: QWidget) -> TypeGuard[TextEditor]:
    return isinstance(widget, (QLineEdit, QPlainTextEdit, QTextEdit))
```

</details>

## 🔧 Function `misspelled_word_at`

```python
def misspelled_word_at(widget: TextEditor, engine: SpellEngine | None = None, *, global_pos: QPoint | None = None) -> tuple[int, int, str] | None
```

Return `(start, end, word)` when the token under the cursor is misspelled.

<details>
<summary>Code:</summary>

```python
def misspelled_word_at(
    widget: TextEditor,
    engine: SpellEngine | None = None,
    *,
    global_pos: QPoint | None = None,
) -> tuple[int, int, str] | None:
    spell = engine if engine is not None else get_spell_engine()
    text = editor_plain_text(widget)
    index = cursor_char_index(widget, global_pos)
    span = word_at_index(text, index)
    if span is None:
        return None
    _start, _end, word = span
    if spell.lookup(word):
        return None
    return span
```

</details>

## 🔧 Function `populate_spellcheck_menu`

```python
def populate_spellcheck_menu(menu: QMenu, widget: TextEditor, *, engine: SpellEngine | None = None, global_pos: QPoint | None = None, on_changed: Callable[[], None] | None = None, suggest_limit: int = _DEFAULT_SUGGEST_LIMIT) -> int
```

Insert suggestions and Add to dictionary at the top of `menu`.

Returns the number of spellcheck actions added (0 when the word is fine).

<details>
<summary>Code:</summary>

```python
def populate_spellcheck_menu(
    menu: QMenu,
    widget: TextEditor,
    *,
    engine: SpellEngine | None = None,
    global_pos: QPoint | None = None,
    on_changed: Callable[[], None] | None = None,
    suggest_limit: int = _DEFAULT_SUGGEST_LIMIT,
) -> int:
    spell = engine if engine is not None else get_spell_engine()
    span = misspelled_word_at(widget, spell, global_pos=global_pos)
    if span is None:
        return 0
    start, end, word = span
    suggestions = spell.suggest(word, limit=suggest_limit)
    insert_before = menu.actions()[0] if menu.actions() else None
    added = 0

    def _notify() -> None:
        if on_changed is not None:
            on_changed()

    for suggestion in suggestions:
        action = QAction(suggestion, menu)
        action.setObjectName("hskSpellcheckSuggestion")

        def _make_replacer(repl: str, s: int, e: int) -> Callable[[], None]:
            def _replace() -> None:
                replace_word_span(widget, s, e, repl)
                _notify()

            return _replace

        action.triggered.connect(_make_replacer(suggestion, start, end))
        if insert_before is not None:
            menu.insertAction(insert_before, action)
        else:
            menu.addAction(action)
        added += 1

    if suggestions:
        separator = menu.insertSeparator(insert_before) if insert_before is not None else menu.addSeparator()
        del separator
        added += 1

    add_action = QAction(f'Add "{word}" to dictionary', menu)
    add_action.setObjectName("hskSpellcheckAddToDictionary")

    def _add() -> None:
        if spell.add_to_user_dictionary(word):
            _notify()

    add_action.triggered.connect(_add)
    if insert_before is not None:
        menu.insertAction(insert_before, add_action)
        menu.insertSeparator(insert_before)
    else:
        menu.addAction(add_action)
        menu.addSeparator()
    added += 2
    return added
```

</details>

## 🔧 Function `popup_spellcheck_menu`

```python
def popup_spellcheck_menu(widget: TextEditor, global_pos: QPoint | None = None, *, engine: SpellEngine | None = None, on_changed: Callable[[], None] | None = None, base_menu: QMenu | None = None) -> bool
```

Show a context menu with suggestions and Add to dictionary when applicable.

<details>
<summary>Code:</summary>

```python
def popup_spellcheck_menu(
    widget: TextEditor,
    global_pos: QPoint | None = None,
    *,
    engine: SpellEngine | None = None,
    on_changed: Callable[[], None] | None = None,
    base_menu: QMenu | None = None,
) -> bool:
    pos = global_pos if global_pos is not None else QCursor.pos()
    if base_menu is not None:
        return populate_spellcheck_menu(base_menu, widget, engine=engine, global_pos=pos, on_changed=on_changed) > 0

    menu = QMenu(widget)
    if populate_spellcheck_menu(menu, widget, engine=engine, global_pos=pos, on_changed=on_changed) == 0:
        menu.deleteLater()
        return False
    menu.exec_(pos)
    return True
```

</details>

## 🔧 Function `replace_word_span`

```python
def replace_word_span(widget: TextEditor, start: int, end: int, replacement: str) -> None
```

Replace characters `[start, end)` in `widget` with `replacement`.

<details>
<summary>Code:</summary>

```python
def replace_word_span(widget: TextEditor, start: int, end: int, replacement: str) -> None:
    if isinstance(widget, QLineEdit):
        text = widget.text()
        widget.setText(text[:start] + replacement + text[end:])
        widget.setCursorPosition(start + len(replacement))
        return
    cursor = widget.textCursor()
    cursor.beginEditBlock()
    cursor.setPosition(start)
    cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
    cursor.insertText(replacement)
    cursor.endEditBlock()
    widget.setTextCursor(cursor)
```

</details>
