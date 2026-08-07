---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_translate_parser.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `align_translations_to_descriptions`](#-function-align_translations_to_descriptions)
- [🔧 Function `parse_transaction_translate_response`](#-function-parse_transaction_translate_response)

</details>

## 🔧 Function `align_translations_to_descriptions`

```python
def align_translations_to_descriptions(descriptions: list[str], translations: dict[str, str]) -> dict[str, str]
```

Map parsed translations onto exact DB description strings (trim-tolerant).

BotHub often returns trimmed description keys while the database still has
leading/trailing spaces, so exact dict lookup would leave preview cells empty.

<details>
<summary>Code:</summary>

```python
def align_translations_to_descriptions(
    descriptions: list[str],
    translations: dict[str, str],
) -> dict[str, str]:
    by_trim: dict[str, str] = {}
    for key, value in translations.items():
        trimmed_key = key.strip()
        trimmed_value = value.strip()
        if trimmed_key and trimmed_value:
            by_trim.setdefault(trimmed_key, trimmed_value)

    aligned: dict[str, str] = {}
    for description in descriptions:
        english = translations.get(description) or by_trim.get(description.strip(), "")
        english = english.strip()
        if description and english:
            aligned[description] = english
    return aligned
```

</details>

## 🔧 Function `parse_transaction_translate_response`

```python
def parse_transaction_translate_response(text: str) -> dict[str, str]
```

Parse Description<TAB>English lines into a translation map.

<details>
<summary>Code:</summary>

````python
def parse_transaction_translate_response(text: str) -> dict[str, str]:
    translations: dict[str, str] = {}
    for raw_line in text.strip().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        parts = line.split("\t")
        if len(parts) != _TSV_COLUMN_COUNT:
            continue
        description = parts[0].strip()
        description_en = parts[1].strip()
        if description and description_en:
            translations[description] = description_en
    return translations
````

</details>
