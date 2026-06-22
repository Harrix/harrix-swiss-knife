---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_translate_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `parse_food_translate_response`](#-function-parse_food_translate_response)
- [🔧 Function `_iter_data_lines`](#-function-_iter_data_lines)

</details>

## 🔧 Function `parse_food_translate_response`

```python
def parse_food_translate_response(text: str) -> dict[str, str]
```

Parse TSV lines Name<TAB>EnglishName into a name-to-translation map.

Args:

- `text` (`str`): Raw BotHub response.

Returns:

- `dict[str, str]`: Russian name to English translation. Empty on parse failure.

<details>
<summary>Code:</summary>

```python
def parse_food_translate_response(text: str) -> dict[str, str]:
    translations: dict[str, str] = {}
    for line in _iter_data_lines(text):
        parts = line.split("\t")
        if len(parts) != _TSV_COLUMN_COUNT:
            continue
        name = parts[0].strip()
        name_en = parts[1].strip()
        if not name or not name_en:
            continue
        translations[name] = name_en
    return translations
```

</details>

## 🔧 Function `_iter_data_lines`

```python
def _iter_data_lines(text: str) -> list[str]
```

Return non-empty lines, skipping markdown code fences.

<details>
<summary>Code:</summary>

````python
def _iter_data_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        lines.append(line)
    return lines
````

</details>
