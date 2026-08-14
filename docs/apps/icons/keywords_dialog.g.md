---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `keywords_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `EditKeywordsDialog`](#%EF%B8%8F-class-editkeywordsdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `get_tags`](#%EF%B8%8F-method-get_tags)

</details>

## 🏛️ Class `EditKeywordsDialog`

```python
class EditKeywordsDialog(QDialog)
```

Modal editor: icon preview on the left, keywords textarea on the right.

<details>
<summary>Code:</summary>

```python
class EditKeywordsDialog(QDialog):

    def __init__(
        self,
        parent: QWidget | None,
        *,
        family: IconFamily,
        icon_path: Path | None,
        app_config: dict[str, Any],
    ) -> None:
        """Build the keywords editor for `family`."""
        super().__init__(parent)
        self._family = family
        self._icon_path = icon_path
        self._app_config = app_config
        self._bothub_state = BothubRequestState()
        self.setWindowTitle("Edit keywords")
        self.setMinimumSize(720, 480)
        qt_modality.set_owner_window_modal(self)
        self._setup_ui()

    def get_tags(self) -> list[str]:
        """Return keywords from the textarea."""
        return parse_keywords_text(self._text_edit.toPlainText())

    def _on_process_with_ai(self) -> None:
        if self._icon_path is None or not self._icon_path.is_file():
            return
        request_keywords_fill(
            self,
            app_config=self._app_config,
            bothub_state=self._bothub_state,
            icon_path=self._icon_path,
            category=", ".join(self._family.categories) or self._family.id,
            tags=self.get_tags(),
            fill_button=self._ai_button,
            on_tags=self._set_tags,
        )

    def _set_tags(self, tags: list[str]) -> None:
        self._text_edit.setPlainText("\n".join(tags))

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        content = QHBoxLayout()

        preview = QLabel()
        preview.setFixedSize(_PREVIEW_SIDE, _PREVIEW_SIDE)
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview.setStyleSheet("QLabel { background-color: #f0f0f0; border-radius: 8px; }")
        if self._icon_path is not None:
            image = render_icon_to_image(self._icon_path, _PREVIEW_SIDE)
            if image is not None and not image.isNull():
                preview.setPixmap(QPixmap.fromImage(image))
        content.addWidget(preview, 0, Qt.AlignmentFlag.AlignTop)

        self._text_edit = QPlainTextEdit()
        self._text_edit.setPlaceholderText("One keyword per line")
        self._text_edit.setPlainText("\n".join(self._family.tags))
        content.addWidget(self._text_edit, 1)
        layout.addLayout(content)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        self._ai_button = make_emoji_push_button("Process with AI", "🤖")
        self._ai_button.setEnabled(self._icon_path is not None and self._icon_path.is_file())
        self._ai_button.clicked.connect(self._on_process_with_ai)
        buttons.addWidget(self._ai_button)

        cancel_button = make_emoji_push_button("Cancel", "❌")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(cancel_button)

        ok_button = make_emoji_push_button("OK", "✅")
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        buttons.addWidget(ok_button)
        layout.addLayout(buttons)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None, *, family: IconFamily, icon_path: Path | None, app_config: dict[str, Any]) -> None
```

Build the keywords editor for `family`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        parent: QWidget | None,
        *,
        family: IconFamily,
        icon_path: Path | None,
        app_config: dict[str, Any],
    ) -> None:
        super().__init__(parent)
        self._family = family
        self._icon_path = icon_path
        self._app_config = app_config
        self._bothub_state = BothubRequestState()
        self.setWindowTitle("Edit keywords")
        self.setMinimumSize(720, 480)
        qt_modality.set_owner_window_modal(self)
        self._setup_ui()
```

</details>

### ⚙️ Method `get_tags`

```python
def get_tags(self) -> list[str]
```

Return keywords from the textarea.

<details>
<summary>Code:</summary>

```python
def get_tags(self) -> list[str]:
        return parse_keywords_text(self._text_edit.toPlainText())
```

</details>
