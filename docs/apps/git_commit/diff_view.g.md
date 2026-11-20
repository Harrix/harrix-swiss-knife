---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `diff_view.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `GitDiffEdit`](#%EF%B8%8F-class-gitdiffedit)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `refresh_theme`](#%EF%B8%8F-method-refresh_theme)
- [🔧 Function `diff_line_kind`](#-function-diff_line_kind)

</details>

## 🏛️ Class `GitDiffEdit`

```python
class GitDiffEdit(FluentPlainTextEdit)
```

Read-only diff with JetBrains Mono and GitHub Desktop-style line colors.

<details>
<summary>Code:</summary>

```python
class GitDiffEdit(FluentPlainTextEdit):

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a diff view."""
        super().__init__(parent)
        apply_mono_font(self)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self._highlighter = _GitDiffHighlighter(self.document(), self)

    def refresh_theme(self) -> None:
        """Re-apply chrome and diff colors."""
        super().refresh_theme()
        # Theme binding runs from `FluentPlainTextEdit.__init__` before the highlighter exists.
        highlighter = getattr(self, "_highlighter", None)
        if highlighter is not None:
            highlighter.rehighlight()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, parent: QWidget | None = None) -> None
```

Create a diff view.

<details>
<summary>Code:</summary>

```python
def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        apply_mono_font(self)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self._highlighter = _GitDiffHighlighter(self.document(), self)
```

</details>

### ⚙️ Method `refresh_theme`

```python
def refresh_theme(self) -> None
```

Re-apply chrome and diff colors.

<details>
<summary>Code:</summary>

```python
def refresh_theme(self) -> None:
        super().refresh_theme()
        # Theme binding runs from `FluentPlainTextEdit.__init__` before the highlighter exists.
        highlighter = getattr(self, "_highlighter", None)
        if highlighter is not None:
            highlighter.rehighlight()
```

</details>

## 🔧 Function `diff_line_kind`

```python
def diff_line_kind(line: str) -> str
```

Return `meta`, `add`, `delete`, `hunk`, or `context` for one diff line.

<details>
<summary>Code:</summary>

```python
def diff_line_kind(line: str) -> str:
    if line.startswith(_META_PREFIXES):
        return "meta"
    if line.startswith("+"):
        return "add"
    if line.startswith("-"):
        return "delete"
    if line.startswith("@@"):
        return "hunk"
    return "context"
```

</details>
