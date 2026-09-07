---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `highlighter.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SpellHighlighter`](#%EF%B8%8F-class-spellhighlighter)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `highlightBlock`](#%EF%B8%8F-method-highlightblock)
  - [⚙️ Method `rehighlight_all`](#%EF%B8%8F-method-rehighlight_all)
  - [⚙️ Method `set_enabled`](#%EF%B8%8F-method-set_enabled)

</details>

## 🏛️ Class `SpellHighlighter`

```python
class SpellHighlighter(QSyntaxHighlighter)
```

Highlight misspelled words with a red wave underline.

<details>
<summary>Code:</summary>

```python
class SpellHighlighter(QSyntaxHighlighter):

    def __init__(self, document: QTextDocument, engine: SpellEngine | None = None) -> None:
        """Attach to `document` using `engine` (default: process-wide)."""
        super().__init__(document)
        self._engine = engine if engine is not None else get_spell_engine()
        self._enabled = True

    def highlightBlock(self, text: str) -> None:  # noqa: N802
        """Underline misspelled tokens in the current block."""
        if not self._enabled or not text:
            return
        engine = self._engine
        for start, end, word in iter_word_spans(text):
            if not engine.lookup(word):
                self.setFormat(start, end - start, _MISS_FORMAT)

    def rehighlight_all(self) -> None:
        """Force a full rehighlight (e.g. after adding a user word)."""
        self.rehighlight()

    def set_enabled(self, *, enabled: bool) -> None:
        """Enable or disable highlighting and rehighlight when turning on."""
        self._enabled = enabled
        if enabled:
            self.rehighlight()
        else:
            self.setDocument(self.document())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, document: QTextDocument, engine: SpellEngine | None = None) -> None
```

Attach to `document` using `engine` (default: process-wide).

<details>
<summary>Code:</summary>

```python
def __init__(self, document: QTextDocument, engine: SpellEngine | None = None) -> None:
        super().__init__(document)
        self._engine = engine if engine is not None else get_spell_engine()
        self._enabled = True
```

</details>

### ⚙️ Method `highlightBlock`

```python
def highlightBlock(self, text: str) -> None
```

Underline misspelled tokens in the current block.

<details>
<summary>Code:</summary>

```python
def highlightBlock(self, text: str) -> None:  # noqa: N802
        if not self._enabled or not text:
            return
        engine = self._engine
        for start, end, word in iter_word_spans(text):
            if not engine.lookup(word):
                self.setFormat(start, end - start, _MISS_FORMAT)
```

</details>

### ⚙️ Method `rehighlight_all`

```python
def rehighlight_all(self) -> None
```

Force a full rehighlight (e.g. after adding a user word).

<details>
<summary>Code:</summary>

```python
def rehighlight_all(self) -> None:
        self.rehighlight()
```

</details>

### ⚙️ Method `set_enabled`

```python
def set_enabled(self, *, enabled: bool) -> None
```

Enable or disable highlighting and rehighlight when turning on.

<details>
<summary>Code:</summary>

```python
def set_enabled(self, *, enabled: bool) -> None:
        self._enabled = enabled
        if enabled:
            self.rehighlight()
        else:
            self.setDocument(self.document())
```

</details>
