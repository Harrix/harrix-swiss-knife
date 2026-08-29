---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `food_translate_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `filter_food_translate_for_names`](#-function-filter_food_translate_for_names)
- [🔧 Function `parse_food_translate_response`](#-function-parse_food_translate_response)

</details>

## 🔧 Function `filter_food_translate_for_names`

```python
def filter_food_translate_for_names(translations: dict[str, str], requested_names: list[str]) -> dict[str, str]
```

Keep translations whose Russian name was in the requested batch.

Args:

- `translations` (`dict[str, str]`): Parsed name → English map.
- `requested_names` (`list[str]`): Names sent to the AI.

Returns:

- `dict[str, str]`: Subset of `translations` for `requested_names` only.

<details>
<summary>Code:</summary>

```python
def filter_food_translate_for_names(
    translations: dict[str, str],
    requested_names: list[str],
) -> dict[str, str]:
    requested = set(requested_names)
    return {name: name_en for name, name_en in translations.items() if name in requested and name_en.strip()}
```

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
