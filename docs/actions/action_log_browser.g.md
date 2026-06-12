---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_log_browser.py`

## 🔧 Function `build_action_output_log_browser`

```python
def build_action_output_log_browser(entries: list[tuple[Path, str]]) -> Callable[[QDialog, QVBoxLayout], None]
```

Return dialog layout builder for recent action log browser.

<details>
<summary>Code:</summary>

```python
def build_action_output_log_browser(
    entries: list[tuple[Path, str]],
    *,
    on_file_selected: Callable[[Path], None] | None,
    show_toast: Callable[[str], None],
) -> Callable[[QDialog, QVBoxLayout], None]:

    def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        list_widget = QListWidget()
        list_widget.setMinimumWidth(280)
        list_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        list_widget.setItemDelegate(ChoiceWithDescriptionDelegate())

        for path, description in entries:
            formatted_description = description.replace("\n", "\n  ")
            item_text = f"{path.name}\n  {formatted_description}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, str(path.resolve()))
            list_widget.addItem(item)

        preview = QPlainTextEdit()
        preview.setReadOnly(True)
        preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        preview_font = QFont("JetBrains Mono")
        preview_font.setPointSize(9)
        preview.setFont(preview_font)

        def load_preview(current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
            if current is None:
                preview.setPlainText("")
                return
            raw = current.data(Qt.ItemDataRole.UserRole)
            if not raw:
                preview.setPlainText("")
                return
            path_obj = Path(str(raw))
            if on_file_selected is not None:
                on_file_selected(path_obj)
            try:
                preview.setPlainText(path_obj.read_text(encoding="utf8"))
            except UnicodeDecodeError as e:
                preview.setPlainText(f"(Could not decode file as UTF-8: {e})")
            except OSError as e:
                preview.setPlainText(f"(Could not read file: {e})")

        list_widget.currentItemChanged.connect(load_preview)

        splitter.addWidget(list_widget)
        splitter.addWidget(preview)
        splitter.setSizes([320, 704])

        layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        copy_button = QPushButton("Copy to Clipboard")

        def click_copy_button() -> None:
            QGuiApplication.clipboard().setText(preview.toPlainText())
            show_toast("Copied to Clipboard")

        copy_button.clicked.connect(click_copy_button)
        button_layout.addWidget(copy_button)
        button_layout.addStretch()

        close_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_box.rejected.connect(dialog.reject)
        button_layout.addWidget(close_box)

        layout.addLayout(button_layout)

        if list_widget.count() > 0:
            list_widget.setCurrentRow(0)

    return _build
```

</details>
