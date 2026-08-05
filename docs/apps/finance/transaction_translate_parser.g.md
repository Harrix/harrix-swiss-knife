---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `transaction_translate_parser.py`

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
