---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `message_box.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_copy_button`](#-function-add_copy_button)
- [🔧 Function `clipboard_text_from_box`](#-function-clipboard_text_from_box)
- [🔧 Function `critical`](#-function-critical)
- [🔧 Function `information`](#-function-information)
- [🔧 Function `prepare_box`](#-function-prepare_box)
- [🔧 Function `question`](#-function-question)
- [🔧 Function `warning`](#-function-warning)

</details>

## 🔧 Function `add_copy_button`

```python
def add_copy_button(box: QMessageBox) -> QAbstractButton
```

Add a Copy button; on click, copy `clipboard_text_from_box` to the clipboard.

<details>
<summary>Code:</summary>

```python
def add_copy_button(box: QMessageBox) -> QAbstractButton:
    copy_btn = box.addButton("Copy", QMessageBox.ButtonRole.ActionRole)
    copy_btn.clicked.disconnect()

    def _copy_box_text() -> None:
        QGuiApplication.clipboard().setText(clipboard_text_from_box(box))

    copy_btn.clicked.connect(_copy_box_text)
    return copy_btn
```

</details>

## 🔧 Function `clipboard_text_from_box`

```python
def clipboard_text_from_box(box: QMessageBox) -> str
```

Build plain text for the clipboard from the dialog fields.

<details>
<summary>Code:</summary>

```python
def clipboard_text_from_box(box: QMessageBox) -> str:
    parts: list[str] = []
    title = box.windowTitle().strip()
    if title:
        parts.append(title)
    body = box.text().strip()
    if body:
        parts.append(body)
    detail = box.detailedText().strip()
    if detail:
        parts.append(detail)
    return "\n\n".join(parts)
```

</details>

## 🔧 Function `critical`

```python
def critical(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton
```

Like `QMessageBox.critical` with a Copy button.

<details>
<summary>Code:</summary>

```python
def critical(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Critical)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return _exec_box(box)
```

</details>

## 🔧 Function `information`

```python
def information(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton
```

Like `QMessageBox.information` with a Copy button.

<details>
<summary>Code:</summary>

```python
def information(
    parent: QWidget | None,
    title: str,
    text: str,
    *,
    stylesheet: str | None = None,
) -> QMessageBox.StandardButton:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    if stylesheet:
        box.setStyleSheet(stylesheet)
    prepare_box(box)
    return _exec_box(box)
```

</details>

## 🔧 Function `prepare_box`

```python
def prepare_box(box: QMessageBox) -> None
```

Ensure `box` has a Copy button (idempotent).

<details>
<summary>Code:</summary>

```python
def prepare_box(box: QMessageBox) -> None:
    if getattr(box, _COPY_BUTTON_ATTR, False):
        return
    add_copy_button(box)
    setattr(box, _COPY_BUTTON_ATTR, True)
```

</details>

## 🔧 Function `question`

```python
def question(parent: QWidget | None, title: str, text: str, buttons: QMessageBox.StandardButton, default_button: QMessageBox.StandardButton) -> QMessageBox.StandardButton
```

Like `QMessageBox.question` with a Copy button.

<details>
<summary>Code:</summary>

```python
def question(
    parent: QWidget | None,
    title: str,
    text: str,
    buttons: QMessageBox.StandardButton,
    default_button: QMessageBox.StandardButton,
) -> QMessageBox.StandardButton:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Question)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(buttons)
    box.setDefaultButton(default_button)
    prepare_box(box)
    return _exec_box(box)
```

</details>

## 🔧 Function `warning`

```python
def warning(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton
```

Like `QMessageBox.warning` with a Copy button.

<details>
<summary>Code:</summary>

```python
def warning(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Warning)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return _exec_box(box)
```

</details>
