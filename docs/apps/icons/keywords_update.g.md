---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `keywords_update.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `parse_keywords_text`](#-function-parse_keywords_text)
- [🔧 Function `replace_frontmatter_list`](#-function-replace_frontmatter_list)
- [🔧 Function `update_keywords_files`](#-function-update_keywords_files)

</details>

## 🔧 Function `parse_keywords_text`

```python
def parse_keywords_text(text: str) -> list[str]
```

Parse keywords from a textarea or AI reply (one item per line).

<details>
<summary>Code:</summary>

````python
def parse_keywords_text(text: str) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        line = _LINE_PREFIX_RE.sub("", line).strip().strip("\"'")
        if not line:
            continue
        key = line.casefold()
        if key in seen:
            continue
        seen.add(key)
        result.append(line)
    return result
````

</details>

## 🔧 Function `replace_frontmatter_list`

```python
def replace_frontmatter_list(text: str, key: str, items: list[str]) -> str
```

Replace a YAML list key in the note frontmatter (inline or block).

<details>
<summary>Code:</summary>

```python
def replace_frontmatter_list(text: str, key: str, items: list[str]) -> str:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        msg = "YAML frontmatter not found"
        raise ValueError(msg)

    frontmatter = match.group(1)
    body = text[match.end() :]
    lines = frontmatter.splitlines()
    new_lines: list[str] = []
    replaced = False
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith(f"{key}:"):
            index += 1
            while index < len(lines) and _LIST_ITEM_RE.match(lines[index]):
                index += 1
            new_lines.extend(_format_yaml_list(key, items))
            replaced = True
            continue
        new_lines.append(lines[index])
        index += 1

    if not replaced:
        new_lines.extend(_format_yaml_list(key, items))

    frontmatter_text = "\n".join(new_lines)
    return f"---\n{frontmatter_text}\n---\n\n{body.lstrip()}\n"
```

</details>

## 🔧 Function `update_keywords_files`

```python
def update_keywords_files(*, md_path: Path, catalog_path: Path, family_id: str, tags: list[str]) -> None
```

Write tags into the note frontmatter and the matching catalog entry.

<details>
<summary>Code:</summary>

```python
def update_keywords_files(
    *,
    md_path: Path,
    catalog_path: Path,
    family_id: str,
    tags: list[str],
) -> None:
    text = md_path.read_text(encoding="utf-8")
    new_markdown = replace_frontmatter_list(text, "tags", tags)

    catalog_text: str | None = None
    new_catalog_text: str | None = None
    if catalog_path.is_file():
        catalog_text = catalog_path.read_text(encoding="utf-8")
        raw = json.loads(catalog_text)
        icons = raw.get("icons") if isinstance(raw, dict) else None
        if not isinstance(icons, list):
            msg = f"Invalid icons list in {catalog_path}"
            raise ValueError(msg)
        matching = [item for item in icons if isinstance(item, dict) and item.get("id") == family_id]
        if not matching:
            msg = f"Icon {family_id!r} not found in {catalog_path}"
            raise ValueError(msg)
        matching[0]["tags"] = list(tags)
        new_catalog_text = json.dumps(raw, ensure_ascii=False, indent=2) + "\n"

    old_markdown = text
    try:
        md_path.write_text(new_markdown, encoding="utf-8")
        if new_catalog_text is not None:
            catalog_path.write_text(new_catalog_text, encoding="utf-8")
    except OSError:
        md_path.write_text(old_markdown, encoding="utf-8")
        if catalog_text is not None:
            catalog_path.write_text(catalog_text, encoding="utf-8")
        raise
```

</details>
