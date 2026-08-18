---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `family_id.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `category_from_family_id`](#-function-category_from_family_id)
- [🔧 Function `family_id_from_stem`](#-function-family_id_from_stem)
- [🔧 Function `native_category_for_family`](#-function-native_category_for_family)
- [🔧 Function `note_dir_for_family_id`](#-function-note_dir_for_family_id)
- [🔧 Function `tags_from_family_id`](#-function-tags_from_family_id)
- [🔧 Function `title_from_family_id`](#-function-title_from_family_id)

</details>

## 🔧 Function `category_from_family_id`

```python
def category_from_family_id(family_id: str) -> str
```

Return category prefix before `__` in a family ID.

<details>
<summary>Code:</summary>

```python
def category_from_family_id(family_id: str) -> str:
    if "__" not in family_id:
        return family_id
    return family_id.split("__", 1)[0]
```

</details>

## 🔧 Function `family_id_from_stem`

```python
def family_id_from_stem(stem: str) -> str
```

Return family ID by stripping variant suffixes from a filename stem.

Removes trailing design index (`_01`), stroke weight (`_line-8`),
`improbable`, and mono color tokens until none remain.

Args:

- `stem` (`str`): Filename without extension, e.g. `building__house_black_01`.

Returns:

- `str`: Family ID such as `building__house`.

<details>
<summary>Code:</summary>

```python
def family_id_from_stem(stem: str) -> str:
    name = stem
    while True:
        changed = False
        for pattern in _STRIP_SUFFIXES:
            new_name = pattern.sub("", name)
            if new_name != name:
                name = new_name
                changed = True
                break
        if not changed:
            break
    return name
```

</details>

## 🔧 Function `native_category_for_family`

```python
def native_category_for_family(family_id: str, categories: list[str] | None = None) -> str
```

Return the folder/filename category for a family (ID prefix, else first YAML).

<details>
<summary>Code:</summary>

```python
def native_category_for_family(family_id: str, categories: list[str] | None = None) -> str:
    if "__" in family_id:
        return category_from_family_id(family_id)
    if categories:
        return str(categories[0]).strip()
    return ""
```

</details>

## 🔧 Function `note_dir_for_family_id`

```python
def note_dir_for_family_id(icons_dir: Path, family_id: str) -> Path
```

Return `icons/{category}/{family_id}` for a family ID.

<details>
<summary>Code:</summary>

```python
def note_dir_for_family_id(icons_dir: Path, family_id: str) -> Path:
    return Path(icons_dir) / category_from_family_id(family_id) / family_id
```

</details>

## 🔧 Function `tags_from_family_id`

```python
def tags_from_family_id(family_id: str) -> list[str]
```

Bootstrap search tags from category and slug tokens.

<details>
<summary>Code:</summary>

```python
def tags_from_family_id(family_id: str) -> list[str]:
    category = category_from_family_id(family_id)
    slug = family_id.split("__", 1)[-1]
    tags: list[str] = []
    seen: set[str] = set()
    for token in (*category.split("_"), *slug.replace("-", " ").split()):
        cleaned = token.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        tags.append(cleaned)
    return tags
```

</details>

## 🔧 Function `title_from_family_id`

```python
def title_from_family_id(family_id: str) -> str
```

Build a human title from the slug after `__`.

<details>
<summary>Code:</summary>

```python
def title_from_family_id(family_id: str) -> str:
    slug = family_id.split("__", 1)[-1]
    return slug.replace("-", " ").replace("_", " ").title()
```

</details>
