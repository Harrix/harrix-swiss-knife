---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `flip_slashes.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFlipSlashes`](#%EF%B8%8F-class-onflipslashes)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
- [🔧 Function `flip_slashes`](#-function-flip_slashes)

</details>

## 🏛️ Class `OnFlipSlashes`

```python
class OnFlipSlashes(ActionBase)
```

Show clipboard text, flip its slashes, and copy the result.

<details>
<summary>Code:</summary>

```python
class OnFlipSlashes(ActionBase):

    icon = "🔀"
    title = "Flip slashes"
    bold_title = False
    cli_available = False
    quick_launcher = True

    @ActionBase.handle_exceptions("flipping slashes")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open a dialog with clipboard text and convert it in place."""
        clipboard = QApplication.clipboard()
        initial = ""
        if clipboard is not None:
            initial = clipboard.text(QClipboard.Mode.Clipboard) or ""
        self._show_dialog(initial)

    def _copy_text(self, text: str) -> None:
        clipboard = QApplication.clipboard()
        if clipboard is None:
            self.show_toast("❌ Clipboard is not available.", duration=4000)
            return
        clipboard.setText(text, QClipboard.Mode.Clipboard)
        self.show_toast("✅ Text copied to clipboard.", duration=2500)

    def _show_dialog(self, initial_text: str) -> None:
        def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
            editor = QPlainTextEdit()
            editor.setPlainText(initial_text)
            editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(editor, stretch=1)

            button_layout = QHBoxLayout()
            convert_button = make_lucide_push_button("Convert", "arrow-left-right")
            style_accept_button(convert_button)
            copy_button = make_lucide_push_button("Copy to Clipboard", COPY_BUTTON_ICON)
            close_button = make_lucide_push_button("Close", "x")

            def convert() -> None:
                converted = flip_slashes(editor.toPlainText())
                editor.setPlainText(converted)
                self._copy_text(converted)

            convert_button.clicked.connect(convert)
            copy_button.clicked.connect(lambda: self._copy_text(editor.toPlainText()))
            close_button.clicked.connect(dialog.reject)
            button_layout.addWidget(convert_button)
            button_layout.addWidget(copy_button)
            button_layout.addStretch(1)
            button_layout.addWidget(close_button)
            layout.addLayout(button_layout)

        self._exec_standard_dialog(self.title, _build, stretch_row=0)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Open a dialog with clipboard text and convert it in place.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        clipboard = QApplication.clipboard()
        initial = ""
        if clipboard is not None:
            initial = clipboard.text(QClipboard.Mode.Clipboard) or ""
        self._show_dialog(initial)
```

</details>

## 🔧 Function `flip_slashes`

```python
def flip_slashes(text: str) -> str
```

Return `text` with slashes flipped to the opposite direction.

- `/` becomes `\`, and a single `\` becomes `/`.
- A doubled `\\` outside a protocol becomes one `\` and is not flipped again.
- `scheme://`, `scheme:\\`, and `\\:` stay as written (`https://`, `https:\\`).

<details>
<summary>Code:</summary>

```python
def flip_slashes(text: str) -> str:
    protected: list[str] = []

    def _protect(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"{_PROTECT_MARK}{len(protected) - 1}{_PROTECT_MARK}"

    converted = _PROTECTED_SLASH_RE.sub(_protect, text)
    converted = converted.replace("\\\\", _ESCAPED_BACKSLASH)
    converted = converted.replace("/", _FORWARD_MARK).replace("\\", "/").replace(_FORWARD_MARK, "\\")
    converted = converted.replace(_ESCAPED_BACKSLASH, "\\")
    for index, original in enumerate(protected):
        converted = converted.replace(f"{_PROTECT_MARK}{index}{_PROTECT_MARK}", original)
    return converted
```

</details>
