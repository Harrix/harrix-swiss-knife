---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text_utils.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `extract_openai_message_content`](#-function-extract_openai_message_content)
- [🔧 Function `strip_markdown_fences`](#-function-strip_markdown_fences)

</details>

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

## 🔧 Function `strip_markdown_fences`

```python
def strip_markdown_fences(text: str) -> str
```

Remove Markdown code fences from model output.

<details>
<summary>Code:</summary>

````python
def strip_markdown_fences(text: str) -> str:
    stripped = text.strip()
    fence_match = re.match(r"^```(?:\w+)?\s*\n?(.*?)\n?```\s*$", stripped, flags=re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped
````

</details>
