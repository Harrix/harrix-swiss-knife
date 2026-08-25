---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `seed.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_recover_sql`](#-function-build_recover_sql)
- [🔧 Function `extract_phrase_emojis`](#-function-extract_phrase_emojis)
- [🔧 Function `seed_emojis`](#-function-seed_emojis)
- [🔧 Function `unique_emojis`](#-function-unique_emojis)

</details>

## 🔧 Function `build_recover_sql`

```python
def build_recover_sql() -> str
```

Return `recover.sql` text for a fresh snippets database.

<details>
<summary>Code:</summary>

```python
def build_recover_sql() -> str:
    lines = [
        "CREATE TABLE items (",
        "  _id INTEGER PRIMARY KEY,",
        "  zone TEXT NOT NULL,",
        "  value TEXT NOT NULL,",
        "  hint TEXT NOT NULL DEFAULT '',",
        "  created_at TEXT NOT NULL,",
        "  last_used_at TEXT,",
        "  sort_index INTEGER NOT NULL DEFAULT 0",
        ");",
        "",
        "CREATE TABLE zone_sort (",
        "  zone TEXT PRIMARY KEY,",
        "  mode TEXT NOT NULL,",
        "  descending INTEGER NOT NULL DEFAULT 0",
        ");",
        "",
    ]
    lines.extend(f"INSERT INTO zone_sort (zone, mode, descending) VALUES ('{zone}', 'alpha', 0);" for zone in ZONES)
    lines.append("")
    lines.extend(_insert_item_sql(ZONE_PHRASE, phrase, "", index) + ";" for index, phrase in enumerate(SEED_PHRASES))
    lines.append("")
    lines.extend(_insert_item_sql(ZONE_EMOJI, emoji, "", index) + ";" for index, emoji in enumerate(seed_emojis()))
    lines.append("")
    lines.extend(
        _insert_item_sql(ZONE_SYMBOL, value, hint, index) + ";" for index, (value, hint) in enumerate(SEED_SYMBOLS)
    )
    lines.append("")
    lines.extend(
        _insert_item_sql(ZONE_COLOR, value, hint, index) + ";" for index, (value, hint) in enumerate(SEED_COLORS)
    )
    lines.append("")
    return "\n".join(lines)
```

</details>

## 🔧 Function `extract_phrase_emojis`

```python
def extract_phrase_emojis(phrases: Sequence[str]) -> list[str]
```

Return leading emoji tokens from phrases, in first-seen order.

<details>
<summary>Code:</summary>

```python
def extract_phrase_emojis(phrases: Sequence[str]) -> list[str]:
    result: list[str] = []
    for phrase in phrases:
        token = phrase.split(" ", 1)[0]
        if token and not token.isascii() and token not in result:
            result.append(token)
    return result
```

</details>

## 🔧 Function `seed_emojis`

```python
def seed_emojis() -> list[str]
```

Return seed emojis: the explicit list plus phrase-only extras.

<details>
<summary>Code:</summary>

```python
def seed_emojis() -> list[str]:
    return unique_emojis(SEED_EMOJIS_BASE, extract_phrase_emojis(SEED_PHRASES))
```

</details>

## 🔧 Function `unique_emojis`

```python
def unique_emojis(*groups: Sequence[str]) -> list[str]
```

Return emojis from `groups` without duplicates, preserving order.

<details>
<summary>Code:</summary>

```python
def unique_emojis(*groups: Sequence[str]) -> list[str]:
    result: list[str] = []
    for group in groups:
        for emoji in group:
            if emoji and emoji not in result:
                result.append(emoji)
    return result
```

</details>
