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
- [🔧 Function `exec_with_copy_retry`](#-function-exec_with_copy_retry)
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

    def on_clicked(button: QAbstractButton) -> None:
        if button is copy_btn:
            QGuiApplication.clipboard().setText(clipboard_text_from_box(box))

    box.buttonClicked.connect(on_clicked)
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
    return exec_with_copy_retry(box)
```

</details>

## 🔧 Function `exec_with_copy_retry`

```python
def exec_with_copy_retry(box: QMessageBox) -> QMessageBox.StandardButton
```

Run `box` until the user clicks a standard button (not Copy).

<details>
<summary>Code:</summary>

```python
def exec_with_copy_retry(box: QMessageBox) -> QMessageBox.StandardButton:
    prepare_box(box)
    copy_btn = _copy_button_for_box[box]
    while True:
        box.exec()
        clicked = box.clickedButton()
        if clicked is copy_btn:
            continue
        if clicked is None:
            return QMessageBox.StandardButton.Cancel
        sb = box.standardButton(clicked)
        return QMessageBox.StandardButton(sb)
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
def information(parent: QWidget | None, title: str, text: str) -> QMessageBox.StandardButton:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(QMessageBox.StandardButton.Ok)
    prepare_box(box)
    return exec_with_copy_retry(box)
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
    if box in _copy_button_for_box:
        return
    _copy_button_for_box[box] = add_copy_button(box)
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
    return exec_with_copy_retry(box)
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
    return exec_with_copy_retry(box)
```

</details>
