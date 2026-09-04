---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_diff_dialog.py`

## 🔧 Function `build_text_diff_side_by_side`

```python
def build_text_diff_side_by_side(before_text: str, after_text: str, default_size: QSize, show_toast: Callable[[str], None], *, rerun_button: bool = False, rerun_button_label: str = RERUN_BUTTON_LABEL, rerun_button_emoji: str = RERUN_BUTTON_EMOJI, remove_paragraphs_button: bool = False, result_text_holder: list[str] | None = None, before_label: str = 'Before', after_label: str = 'After', highlight_changes: bool = True) -> Callable[[QDialog, QVBoxLayout], None]
```

Return dialog layout builder for before/after diff view.

<details>
<summary>Code:</summary>

```python
def build_text_diff_side_by_side(
    before_text: str,
    after_text: str,
    default_size: QSize,
    show_toast: Callable[[str], None],
    *,
    rerun_button: bool = False,
    rerun_button_label: str = RERUN_BUTTON_LABEL,
    rerun_button_emoji: str = RERUN_BUTTON_EMOJI,
    remove_paragraphs_button: bool = False,
    result_text_holder: list[str] | None = None,
    before_label: str = "Before",
    after_label: str = "After",
    highlight_changes: bool = True,
) -> Callable[[QDialog, QVBoxLayout], None]:

    def _make_selection(
        doc: QTextDocument,
        *,
        line_no: int,
        start_col: int = 0,
        end_col: int | None = None,
        fmt: QTextCharFormat,
    ) -> QTextEdit.ExtraSelection | None:
        block = doc.findBlockByNumber(line_no)
        if not block.isValid():
            return None
        text = block.text()
        end = len(text) if end_col is None else max(0, min(end_col, len(text)))
        start = max(0, min(start_col, end))

        cursor = QTextCursor(doc)
        cursor.setPosition(block.position() + start)
        cursor.setPosition(block.position() + end, QTextCursor.MoveMode.KeepAnchor)

        sel = QTextEdit.ExtraSelection()
        sel.cursor = cursor
        sel.format = fmt
        return sel

    def _format_with_bg(bg: QColor) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setBackground(bg)
        return fmt

    def _build(dialog: QDialog, layout: QVBoxLayout) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_label = QLabel(before_label)
        left_layout.addWidget(left_label)

        before_edit = QPlainTextEdit()
        before_edit.setPlainText(before_text)
        before_edit.setReadOnly(True)
        before_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Keep the content readable for long lines.
        before_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        font = QFont()
        font.setPointSize(9)
        before_edit.setFont(font)
        fit_widget_height(
            before_edit,
            text_content_height(before_edit),
            maximum=default_size.height() - 120,
        )
        left_layout.addWidget(before_edit)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_label = QLabel(after_label)
        right_layout.addWidget(right_label)

        after_edit = QPlainTextEdit()
        after_edit.setPlainText(after_text)
        after_edit.setReadOnly(True)
        after_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        after_edit.setFont(font)
        after_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        fit_widget_height(
            after_edit,
            text_content_height(after_edit),
            maximum=default_size.height() - 120,
        )
        right_layout.addWidget(after_edit)

        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([512, 512])
        layout.addWidget(splitter)

        if highlight_changes:
            _apply_diff_highlights(before_edit, after_edit, before_text, after_text, _make_selection, _format_with_bg)

        # Sync vertical scrollbars so user can compare line positions.
        syncing = False

        def sync_from_before(value: int) -> None:
            nonlocal syncing
            if syncing:
                return
            syncing = True
            after_edit.verticalScrollBar().setValue(value)
            syncing = False

        def sync_from_after(value: int) -> None:
            nonlocal syncing
            if syncing:
                return
            syncing = True
            before_edit.verticalScrollBar().setValue(value)
            syncing = False

        before_edit.verticalScrollBar().valueChanged.connect(sync_from_before)
        after_edit.verticalScrollBar().valueChanged.connect(sync_from_after)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        def click_copy_button() -> None:
            QGuiApplication.clipboard().setText(after_edit.toPlainText())
            show_toast("Copied to Clipboard")

        add_copy_button(button_layout, click_copy_button)

        def on_remove_paragraphs() -> None:
            collapsed = collapse_text_to_single_line(after_edit.toPlainText())
            after_edit.setPlainText(collapsed)
            after_edit.setExtraSelections([])
            QGuiApplication.clipboard().setText(collapsed)
            if result_text_holder is not None:
                result_text_holder[0] = collapsed
            show_toast("Converted to single line")
            if remove_paragraphs_btn is not None:
                remove_paragraphs_btn.setVisible(False)

        remove_paragraphs_btn = append_result_action_buttons(
            dialog,
            button_layout,
            rerun_button=rerun_button,
            rerun_button_label=rerun_button_label,
            rerun_button_emoji=rerun_button_emoji,
            remove_paragraphs_button=remove_paragraphs_button,
            on_remove_paragraphs=on_remove_paragraphs if remove_paragraphs_button else None,
            remove_paragraphs_source_text=after_text,
        )

        add_ok_button(dialog, button_layout)

        layout.addLayout(button_layout)

    return _build
```

</details>
