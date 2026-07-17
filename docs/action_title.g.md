---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_title.py`

## 🔧 Function `strip_md_inline_code_markers`

```python
def strip_md_inline_code_markers(text: str) -> str
```

Remove Markdown backtick markers for plain Qt UI display.

Example: strip inner backticks so `config.json` displays without markers.

<details>
<summary>Code:</summary>

```python
def strip_md_inline_code_markers(text: str) -> str:
    return text.replace("`", "")
```

</details>
