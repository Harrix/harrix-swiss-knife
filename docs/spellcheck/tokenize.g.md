---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tokenize.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `iter_skip_spans`](#-function-iter_skip_spans)
- [🔧 Function `iter_word_spans`](#-function-iter_word_spans)
- [🔧 Function `word_at_index`](#-function-word_at_index)

</details>

## 🔧 Function `iter_skip_spans`

```python
def iter_skip_spans(text: str) -> list[tuple[int, int]]
```

Return `[start, end)` spans that must not be spellchecked.

<details>
<summary>Code:</summary>

```python
def iter_skip_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in _SKIP_RUN_RE.finditer(text)]
```

</details>

## 🔧 Function `iter_word_spans`

```python
def iter_word_spans(text: str) -> list[tuple[int, int, str]]
```

Return `(start, end, word)` spans for spellcheckable tokens in `text`.

Words may contain letters, digits, and internal `'` / `-`. Pure digit tokens,
and tokens inside URL/email/path runs, are omitted.

<details>
<summary>Code:</summary>

```python
def iter_word_spans(text: str) -> list[tuple[int, int, str]]:
    skip_spans = iter_skip_spans(text)
    spans: list[tuple[int, int, str]] = []
    for match in _WORD_RE.finditer(text):
        start, end = match.start(), match.end()
        if _in_skip(start, skip_spans):
            continue
        word = match.group(0)
        if _DIGITS_ONLY_RE.fullmatch(word):
            continue
        spans.append((start, end, word))
    return spans
```

</details>

## 🔧 Function `word_at_index`

```python
def word_at_index(text: str, index: int) -> tuple[int, int, str] | None
```

Return the word span covering `index`, or `None` if there is none.

When `index` sits on a boundary (typical caret after a word), the word to the
left is preferred.

<details>
<summary>Code:</summary>

```python
def word_at_index(text: str, index: int) -> tuple[int, int, str] | None:
    if index < 0 or index > len(text):
        return None
    spans = iter_word_spans(text)
    for start, end, word in spans:
        if start <= index < end:
            return start, end, word
    if index > 0:
        for start, end, word in spans:
            if start <= index - 1 < end:
                return start, end, word
    return None
```

</details>
