---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_result_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_copy_button`](#-function-add_copy_button)
- [🔧 Function `add_ok_button`](#-function-add_ok_button)
- [🔧 Function `append_result_action_buttons`](#-function-append_result_action_buttons)
- [🔧 Function `collapse_text_to_single_line`](#-function-collapse_text_to_single_line)
- [🔧 Function `resolve_text_result_dialog_action`](#-function-resolve_text_result_dialog_action)

</details>

## 🔧 Function `add_copy_button`

```python
def add_copy_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton
```

Add a copy-to-clipboard button with an emoji icon.

<details>
<summary>Code:</summary>

```python
def add_copy_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton:
    copy_button = make_emoji_push_button(COPY_BUTTON_LABEL, COPY_BUTTON_EMOJI)
    copy_button.clicked.connect(click_handler)
    button_layout.addWidget(copy_button)
    return copy_button
```

</details>

## 🔧 Function `add_ok_button`

```python
def add_ok_button(dialog: QDialog, button_layout: QHBoxLayout) -> QPushButton
```

Add an OK button with an emoji icon.

<details>
<summary>Code:</summary>

```python
def add_ok_button(dialog: QDialog, button_layout: QHBoxLayout) -> QPushButton:
    ok_button = make_emoji_push_button(OK_BUTTON_LABEL, OK_BUTTON_EMOJI)
    ok_button.clicked.connect(dialog.accept)
    button_layout.addWidget(ok_button)
    return ok_button
```

</details>

## 🔧 Function `append_result_action_buttons`

```python
def append_result_action_buttons(dialog: QDialog, button_layout: QHBoxLayout) -> None
```

Add optional rerun/rewrite/remove-paragraphs buttons that close the dialog with custom codes.

<details>
<summary>Code:</summary>

```python
def append_result_action_buttons(
    dialog: QDialog,
    button_layout: QHBoxLayout,
    *,
    rerun_button: bool = False,
    rerun_button_label: str = RERUN_BUTTON_LABEL,
    rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
    rewrite_button: bool = False,
    remove_paragraphs_button: bool = False,
) -> None:
    if rerun_button:
        rerun_btn = make_emoji_push_button(rerun_button_label, rerun_button_emoji)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = make_emoji_push_button(REWRITE_BUTTON_LABEL, REWRITE_BUTTON_EMOJI)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)

    if remove_paragraphs_button:
        remove_paragraphs_btn = make_emoji_push_button(
            REMOVE_PARAGRAPHS_BUTTON_LABEL,
            REMOVE_PARAGRAPHS_BUTTON_EMOJI,
        )
        remove_paragraphs_btn.clicked.connect(lambda: dialog.done(REMOVE_PARAGRAPHS_DIALOG_CODE))
        button_layout.addWidget(remove_paragraphs_btn)
```

</details>

## 🔧 Function `collapse_text_to_single_line`

```python
def collapse_text_to_single_line(text: str) -> str
```

Replace line breaks and paragraph gaps with single spaces.

<details>
<summary>Code:</summary>

```python
def collapse_text_to_single_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()
```

</details>

## 🔧 Function `resolve_text_result_dialog_action`

```python
def resolve_text_result_dialog_action(action_code: int, current_text: str) -> str | None
```

Handle custom dialog codes. Return updated text to continue the loop, or None to stop.

<details>
<summary>Code:</summary>

```python
def resolve_text_result_dialog_action(
    action_code: int,
    current_text: str,
    *,
    on_rerun: Callable[[], None] | None = None,
    on_rewrite: Callable[[], None] | None = None,
) -> str | None:
    if action_code == RERUN_DIALOG_CODE:
        if on_rerun is not None:
            on_rerun()
        return None
    if action_code == REWRITE_DIALOG_CODE:
        if on_rewrite is not None:
            on_rewrite()
        return None
    if action_code == REMOVE_PARAGRAPHS_DIALOG_CODE:
        return collapse_text_to_single_line(current_text)
    return None
```

</details>
