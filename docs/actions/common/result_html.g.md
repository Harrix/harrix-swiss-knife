---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `result_html.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ResultTextBrowser`](#%EF%B8%8F-class-resulttextbrowser)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `createMimeDataFromSelection`](#%EF%B8%8F-method-createmimedatafromselection)
  - [⚙️ Method `set_plain_result`](#%EF%B8%8F-method-set_plain_result)
- [🔧 Function `plain_text_to_result_html`](#-function-plain_text_to_result_html)

</details>

## 🏛️ Class `ResultTextBrowser`

```python
class ResultTextBrowser(QTextBrowser)
```

Read-only result view: clickable links, clipboard selections stay plain text.

<details>
<summary>Code:</summary>

```python
class ResultTextBrowser(QTextBrowser):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a result browser that opens http(s) links in the default browser."""
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        self.setUndoRedoEnabled(False)
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        self.document().setDefaultFont(font)
        self.document().setDefaultStyleSheet(_LINK_STYLE)

    def createMimeDataFromSelection(self) -> QMimeData:  # noqa: N802
        """Copy the selected characters only, without HTML link markup."""
        mime = QMimeData()
        mime.setText(self.textCursor().selectedText().replace("\u2029", "\n"))
        return mime

    def set_plain_result(self, text: str) -> None:
        """Show `text` with auto-linked URLs."""
        self.setHtml(plain_text_to_result_html(text))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a result browser that opens http(s) links in the default browser.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setOpenExternalLinks(True)
        self.setOpenLinks(True)
        self.setUndoRedoEnabled(False)
        font = QFont()
        font.setPointSize(9)
        self.setFont(font)
        self.document().setDefaultFont(font)
        self.document().setDefaultStyleSheet(_LINK_STYLE)
```

</details>

### ⚙️ Method `createMimeDataFromSelection`

```python
def createMimeDataFromSelection(self) -> QMimeData
```

Copy the selected characters only, without HTML link markup.

<details>
<summary>Code:</summary>

```python
def createMimeDataFromSelection(self) -> QMimeData:  # noqa: N802
        mime = QMimeData()
        mime.setText(self.textCursor().selectedText().replace("\u2029", "\n"))
        return mime
```

</details>

### ⚙️ Method `set_plain_result`

```python
def set_plain_result(self, text: str) -> None
```

Show `text` with auto-linked URLs.

<details>
<summary>Code:</summary>

```python
def set_plain_result(self, text: str) -> None:
        self.setHtml(plain_text_to_result_html(text))
```

</details>

## 🔧 Function `plain_text_to_result_html`

```python
def plain_text_to_result_html(text: str) -> str
```

Escape `text` and wrap http(s) URLs in blue underlined anchors.

Trailing sentence punctuation is kept outside the link. The visible URL text
stays the same as in the log so `QTextBrowser.toPlainText()` matches `text`.

<details>
<summary>Code:</summary>

```python
def plain_text_to_result_html(text: str) -> str:
    chunks: list[str] = []
    pos = 0
    for match in _URL_RE.finditer(text):
        url, trailing = _split_trailing_url_punct(match.group())
        chunks.append(html.escape(text[pos : match.start()]))
        if url:
            escaped = html.escape(url, quote=True)
            chunks.append(f'<a href="{escaped}">{html.escape(url)}</a>')
        chunks.append(html.escape(trailing))
        pos = match.end()
    chunks.append(html.escape(text[pos:]))
    body = "".join(chunks)
    return f"<html><head><meta charset='utf-8'></head><body style='white-space:pre-wrap;margin:0;'>{body}</body></html>"
```

</details>
