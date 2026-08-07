---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_result_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `RERUN_DIALOG_CODE`](#-constant-rerun_dialog_code)
- [📎 Constant `REWRITE_DIALOG_CODE`](#-constant-rewrite_dialog_code)
- [📎 Constant `RERUN_BUTTON_LABEL`](#-constant-rerun_button_label)
- [📎 Constant `RERUN_BUTTON_EMOJI`](#-constant-rerun_button_emoji)
- [📎 Constant `FIX_AGAIN_BUTTON_LABEL`](#-constant-fix_again_button_label)
- [📎 Constant `FIX_AGAIN_BUTTON_EMOJI`](#-constant-fix_again_button_emoji)
- [📎 Constant `REWRITE_AGAIN_BUTTON_LABEL`](#-constant-rewrite_again_button_label)
- [📎 Constant `REWRITE_AGAIN_BUTTON_EMOJI`](#-constant-rewrite_again_button_emoji)
- [📎 Constant `REWRITE_BUTTON_LABEL`](#-constant-rewrite_button_label)
- [📎 Constant `REWRITE_BUTTON_EMOJI`](#-constant-rewrite_button_emoji)
- [📎 Constant `REMOVE_PARAGRAPHS_BUTTON_LABEL`](#-constant-remove_paragraphs_button_label)
- [📎 Constant `REMOVE_PARAGRAPHS_BUTTON_EMOJI`](#-constant-remove_paragraphs_button_emoji)
- [📎 Constant `COPY_BUTTON_LABEL`](#-constant-copy_button_label)
- [📎 Constant `COPY_BUTTON_EMOJI`](#-constant-copy_button_emoji)
- [📎 Constant `OPEN_FOLDER_BUTTON_LABEL`](#-constant-open_folder_button_label)
- [📎 Constant `OPEN_FOLDER_BUTTON_EMOJI`](#-constant-open_folder_button_emoji)
- [📎 Constant `OK_BUTTON_LABEL`](#-constant-ok_button_label)
- [📎 Constant `OK_BUTTON_EMOJI`](#-constant-ok_button_emoji)
- [📎 Constant `CANCEL_BUTTON_EMOJI`](#-constant-cancel_button_emoji)
- [🔧 Function `add_copy_button`](#-function-add_copy_button)
- [🔧 Function `add_ok_button`](#-function-add_ok_button)
- [🔧 Function `add_open_folder_button`](#-function-add_open_folder_button)
- [🔧 Function `append_result_action_buttons`](#-function-append_result_action_buttons)
- [🔧 Function `collapse_text_to_single_line`](#-function-collapse_text_to_single_line)
- [🔧 Function `resolve_text_result_dialog_action`](#-function-resolve_text_result_dialog_action)

</details>

## 📎 Constant `RERUN_DIALOG_CODE`

```python
RERUN_DIALOG_CODE = 2
```

_No docstring provided._

## 📎 Constant `REWRITE_DIALOG_CODE`

```python
REWRITE_DIALOG_CODE = 3
```

_No docstring provided._

## 📎 Constant `RERUN_BUTTON_LABEL`

```python
RERUN_BUTTON_LABEL = 'Run again'
```

_No docstring provided._

## 📎 Constant `RERUN_BUTTON_EMOJI`

```python
RERUN_BUTTON_EMOJI = '🔄'
```

_No docstring provided._

## 📎 Constant `FIX_AGAIN_BUTTON_LABEL`

```python
FIX_AGAIN_BUTTON_LABEL = 'Fix again'
```

_No docstring provided._

## 📎 Constant `FIX_AGAIN_BUTTON_EMOJI`

```python
FIX_AGAIN_BUTTON_EMOJI = '🤖'
```

_No docstring provided._

## 📎 Constant `REWRITE_AGAIN_BUTTON_LABEL`

```python
REWRITE_AGAIN_BUTTON_LABEL = 'Rewrite again'
```

_No docstring provided._

## 📎 Constant `REWRITE_AGAIN_BUTTON_EMOJI`

```python
REWRITE_AGAIN_BUTTON_EMOJI = '✍️'
```

_No docstring provided._

## 📎 Constant `REWRITE_BUTTON_LABEL`

```python
REWRITE_BUTTON_LABEL = 'Rewrite with AI…'
```

_No docstring provided._

## 📎 Constant `REWRITE_BUTTON_EMOJI`

```python
REWRITE_BUTTON_EMOJI = '✍️'
```

_No docstring provided._

## 📎 Constant `REMOVE_PARAGRAPHS_BUTTON_LABEL`

```python
REMOVE_PARAGRAPHS_BUTTON_LABEL = 'To single line'
```

_No docstring provided._

## 📎 Constant `REMOVE_PARAGRAPHS_BUTTON_EMOJI`

```python
REMOVE_PARAGRAPHS_BUTTON_EMOJI = '↪️'
```

_No docstring provided._

## 📎 Constant `COPY_BUTTON_LABEL`

```python
COPY_BUTTON_LABEL = 'Copy to Clipboard'
```

_No docstring provided._

## 📎 Constant `COPY_BUTTON_EMOJI`

```python
COPY_BUTTON_EMOJI = '📋'
```

_No docstring provided._

## 📎 Constant `OPEN_FOLDER_BUTTON_LABEL`

```python
OPEN_FOLDER_BUTTON_LABEL = 'Open folder'
```

_No docstring provided._

## 📎 Constant `OPEN_FOLDER_BUTTON_EMOJI`

```python
OPEN_FOLDER_BUTTON_EMOJI = '📂'
```

_No docstring provided._

## 📎 Constant `OK_BUTTON_LABEL`

```python
OK_BUTTON_LABEL = 'OK'
```

_No docstring provided._

## 📎 Constant `OK_BUTTON_EMOJI`

```python
OK_BUTTON_EMOJI = '✅'
```

_No docstring provided._

## 📎 Constant `CANCEL_BUTTON_EMOJI`

```python
CANCEL_BUTTON_EMOJI = '❌'
```

_No docstring provided._

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

## 🔧 Function `add_open_folder_button`

```python
def add_open_folder_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton
```

Add an open-folder button with an emoji icon.

<details>
<summary>Code:</summary>

```python
def add_open_folder_button(button_layout: QHBoxLayout, click_handler: Callable[[], None]) -> QPushButton:
    open_folder_button = make_emoji_push_button(OPEN_FOLDER_BUTTON_LABEL, OPEN_FOLDER_BUTTON_EMOJI)
    open_folder_button.clicked.connect(click_handler)
    button_layout.addWidget(open_folder_button)
    return open_folder_button
```

</details>

## 🔧 Function `append_result_action_buttons`

```python
def append_result_action_buttons(dialog: QDialog, button_layout: QHBoxLayout, *, rerun_button: bool = False, rerun_button_label: str = RERUN_BUTTON_LABEL, rerun_button_emoji: str = RERUN_BUTTON_EMOJI, rewrite_button: bool = False, remove_paragraphs_button: bool = False, on_remove_paragraphs: Callable[[], None] | None = None) -> None
```

Add optional rerun/rewrite buttons and in-place remove-paragraphs action.

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
    on_remove_paragraphs: Callable[[], None] | None = None,
) -> None:
    if rerun_button:
        rerun_btn = make_emoji_push_button(rerun_button_label, rerun_button_emoji)
        rerun_btn.clicked.connect(lambda: dialog.done(RERUN_DIALOG_CODE))
        button_layout.addWidget(rerun_btn)

    if rewrite_button:
        rewrite_btn = make_emoji_push_button(REWRITE_BUTTON_LABEL, REWRITE_BUTTON_EMOJI)
        rewrite_btn.clicked.connect(lambda: dialog.done(REWRITE_DIALOG_CODE))
        button_layout.addWidget(rewrite_btn)

    if remove_paragraphs_button and on_remove_paragraphs is not None:
        remove_paragraphs_btn = make_emoji_push_button(
            REMOVE_PARAGRAPHS_BUTTON_LABEL,
            REMOVE_PARAGRAPHS_BUTTON_EMOJI,
        )
        remove_paragraphs_btn.clicked.connect(on_remove_paragraphs)
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
def resolve_text_result_dialog_action(action_code: int, _current_text: str, *, on_rerun: Callable[[], None] | None = None, on_rewrite: Callable[[], None] | None = None) -> str | None
```

Handle custom dialog codes. Always returns `None` after optional callbacks.

<details>
<summary>Code:</summary>

```python
def resolve_text_result_dialog_action(
    action_code: int,
    _current_text: str,
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
    return None
```

</details>
