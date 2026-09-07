---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `user_dict.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_user_word`](#-function-add_user_word)
- [🔧 Function `load_user_words`](#-function-load_user_words)
- [🔧 Function `save_user_words`](#-function-save_user_words)

</details>

## 🔧 Function `add_user_word`

```python
def add_user_word(word: str, path: Path | None = None) -> set[str]
```

Add `word` to the user dictionary and return the updated set.

Empty or whitespace-only words are ignored.

<details>
<summary>Code:</summary>

```python
def add_user_word(word: str, path: Path | None = None) -> set[str]:
    cleaned = word.strip()
    words = load_user_words(path)
    if not cleaned:
        return words
    if cleaned in words:
        return words
    words.add(cleaned)
    save_user_words(words, path)
    return words
```

</details>

## 🔧 Function `load_user_words`

```python
def load_user_words(path: Path | None = None) -> set[str]
```

Load unique non-empty words from the user dictionary file.

<details>
<summary>Code:</summary>

```python
def load_user_words(path: Path | None = None) -> set[str]:
    dict_path = path if path is not None else get_spellcheck_user_dict_path()
    if not dict_path.is_file():
        return set()
    words: set[str] = set()
    text = dict_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        word = line.strip()
        if word and not word.startswith("#"):
            words.add(word)
    return words
```

</details>

## 🔧 Function `save_user_words`

```python
def save_user_words(words: set[str], path: Path | None = None) -> None
```

Write sorted unique words to the user dictionary file (UTF-8).

<details>
<summary>Code:</summary>

```python
def save_user_words(words: set[str], path: Path | None = None) -> None:
    dict_path = path if path is not None else get_spellcheck_user_dict_path()
    dict_path.parent.mkdir(parents=True, exist_ok=True)
    lines = sorted(words, key=lambda w: (w.casefold(), w))
    dict_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
```

</details>
