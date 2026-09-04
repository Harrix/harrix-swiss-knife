---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `decode_musicbee_text`](#-function-decode_musicbee_text)
- [🔧 Function `normalize_path_key`](#-function-normalize_path_key)
- [🔧 Function `path_is_under`](#-function-path_is_under)

</details>

## 🔧 Function `decode_musicbee_text`

```python
def decode_musicbee_text(raw: bytes) -> str
```

Decode a MusicBee path or tag, preferring UTF-8 then the system ANSI code page.

<details>
<summary>Code:</summary>

```python
def decode_musicbee_text(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1251", errors="replace")
```

</details>

## 🔧 Function `normalize_path_key`

```python
def normalize_path_key(path: str | Path) -> str
```

Return a casefolded Windows-style key for path comparison.

<details>
<summary>Code:</summary>

```python
def normalize_path_key(path: str | Path) -> str:
    text = str(path).replace("/", "\\").strip()
    while text.endswith("\\") and not text.endswith(":\\"):
        text = text[:-1]
    return text.casefold()
```

</details>

## 🔧 Function `path_is_under`

```python
def path_is_under(path: str | Path, folder: str | Path) -> bool
```

Return whether `path` is `folder` or a descendant.

Uses resolved paths when both exist; otherwise compares normalized prefixes
so missing playlist entries can still be filtered.

<details>
<summary>Code:</summary>

```python
def path_is_under(path: str | Path, folder: str | Path) -> bool:
    candidate = Path(path)
    root = Path(folder)
    if candidate.exists() and root.exists():
        try:
            candidate.resolve().relative_to(root.resolve())
        except ValueError:
            return False
        return True
    key = normalize_path_key(candidate)
    root_key = normalize_path_key(root)
    return key == root_key or key.startswith(f"{root_key}\\")
```

</details>
