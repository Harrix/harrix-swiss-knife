"""Side-by-side text diff dialog builder."""

from __future__ import annotations

import difflib
from collections.abc import Callable

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QGuiApplication, QTextCharFormat, QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


def build_text_diff_side_by_side(
    before_text: str,
    after_text: str,
    default_size: QSize,
    show_toast: Callable[[str], None],
) -> Callable[[QDialog, QVBoxLayout], None]:
    """Return dialog layout builder for before/after diff view."""

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
        left_label = QLabel("Before")
        left_layout.addWidget(left_label)

        before_edit = QPlainTextEdit()
        before_edit.setPlainText(before_text)
        before_edit.setReadOnly(True)
        before_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        before_edit.setMinimumHeight(default_size.height() - 120)
        # Keep the content readable for long lines.
        before_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)

        font = QFont("JetBrains Mono")
        font.setPointSize(9)
        before_edit.setFont(font)
        left_layout.addWidget(before_edit)

        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_label = QLabel("After")
        right_layout.addWidget(right_label)

        after_edit = QPlainTextEdit()
        after_edit.setPlainText(after_text)
        after_edit.setReadOnly(True)
        after_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        after_edit.setMinimumHeight(default_size.height() - 120)
        after_edit.setFont(font)
        after_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        right_layout.addWidget(after_edit)

        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([512, 512])
        layout.addWidget(splitter)

        # Mergely-like highlighting:
        # - whole-line background only for inserted/deleted lines
        # - inline background for changed segments; equal text stays unstyled
        before_lines = before_text.splitlines()
        after_lines = after_text.splitlines()
        matcher = difflib.SequenceMatcher(a=before_lines, b=after_lines)

        del_line_bg = QColor(255, 80, 80, 170)  # red-ish
        ins_line_bg = QColor(60, 200, 60, 170)  # green-ish

        del_inline_bg = QColor(255, 80, 80, 210)
        ins_inline_bg = QColor(60, 200, 60, 210)
        repl_inline_bg = QColor(255, 200, 60, 210)

        before_doc = before_edit.document()
        after_doc = after_edit.document()

        before_selections: list[QTextEdit.ExtraSelection] = []
        after_selections: list[QTextEdit.ExtraSelection] = []

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            if tag == "delete":
                line_fmt = _format_with_bg(del_line_bg)
                for ln in range(i1, i2):
                    sel = _make_selection(before_doc, line_no=ln, fmt=line_fmt)
                    if sel is not None:
                        before_selections.append(sel)
                continue

            if tag == "insert":
                line_fmt = _format_with_bg(ins_line_bg)
                for ln in range(j1, j2):
                    sel = _make_selection(after_doc, line_no=ln, fmt=line_fmt)
                    if sel is not None:
                        after_selections.append(sel)
                continue

            # replace: highlight only changed segments, not unchanged parts of a line
            left_span = i2 - i1
            right_span = j2 - j1
            pairs = max(left_span, right_span)

            for k in range(pairs):
                left_ln = i1 + k
                right_ln = j1 + k
                left_line = before_lines[left_ln] if left_ln < i2 else ""
                right_line = after_lines[right_ln] if right_ln < j2 else ""

                # If one side is missing (because spans differ), treat as full insert/delete.
                if left_ln >= i2 and right_ln < j2:
                    sel = _make_selection(after_doc, line_no=right_ln, fmt=_format_with_bg(ins_inline_bg))
                    if sel is not None:
                        after_selections.append(sel)
                    continue
                if right_ln >= j2 and left_ln < i2:
                    sel = _make_selection(before_doc, line_no=left_ln, fmt=_format_with_bg(del_inline_bg))
                    if sel is not None:
                        before_selections.append(sel)
                    continue

                inline = difflib.SequenceMatcher(a=left_line, b=right_line)
                for itag, ai1, ai2, bi1, bi2 in inline.get_opcodes():
                    if itag == "equal":
                        continue
                    if itag == "delete":
                        sel = _make_selection(
                            before_doc,
                            line_no=left_ln,
                            start_col=ai1,
                            end_col=ai2,
                            fmt=_format_with_bg(del_inline_bg),
                        )
                        if sel is not None:
                            before_selections.append(sel)
                    elif itag == "insert":
                        sel = _make_selection(
                            after_doc,
                            line_no=right_ln,
                            start_col=bi1,
                            end_col=bi2,
                            fmt=_format_with_bg(ins_inline_bg),
                        )
                        if sel is not None:
                            after_selections.append(sel)
                    else:  # replace
                        sel = _make_selection(
                            before_doc,
                            line_no=left_ln,
                            start_col=ai1,
                            end_col=ai2,
                            fmt=_format_with_bg(repl_inline_bg),
                        )
                        if sel is not None:
                            before_selections.append(sel)
                        sel = _make_selection(
                            after_doc,
                            line_no=right_ln,
                            start_col=bi1,
                            end_col=bi2,
                            fmt=_format_with_bg(repl_inline_bg),
                        )
                        if sel is not None:
                            after_selections.append(sel)

        # Apply selections after layout is ready to avoid cases where the first paint drops them.
        def apply_highlight() -> None:
            before_edit.setExtraSelections(before_selections)
            after_edit.setExtraSelections(after_selections)

        QTimer.singleShot(0, apply_highlight)

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
        copy_button = QPushButton("Copy to Clipboard")

        def click_copy_button() -> None:
            QGuiApplication.clipboard().setText(after_edit.toPlainText())
            show_toast("Copied to Clipboard")

        copy_button.clicked.connect(click_copy_button)
        button_layout.addWidget(copy_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

    return _build
