---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_utils.py`

## 🔧 Function `extract_openai_message_content`

```python
def extract_openai_message_content(content: Any) -> str
```

Extract plain text from OpenAI-style message content.

<details>
<summary>Code:</summary>

```python
def extract_openai_message_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text", "")))
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return str(content)
```

</details>
