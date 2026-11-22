---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `russian_word_forms.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_russian_word_forms_prompt`](#-function-build_russian_word_forms_prompt)
- [🔧 Function `get_russian_word_forms_prompt_template`](#-function-get_russian_word_forms_prompt_template)
- [🔧 Function `parse_russian_word_forms`](#-function-parse_russian_word_forms)

</details>

## 🔧 Function `build_russian_word_forms_prompt`

```python
def build_russian_word_forms_prompt(word: str, config: dict[str, Any]) -> str
```

Build the word-forms prompt for `word`.

Raises:

- `ValueError`: If the prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_russian_word_forms_prompt(word: str, config: dict[str, Any]) -> str:
    return build_prompt(
        config,
        PROMPT_KEY,
        {"WORD": word.strip()},
        prompt_display_name=PROMPT_KEY,
    )
```

</details>

## 🔧 Function `get_russian_word_forms_prompt_template`

```python
def get_russian_word_forms_prompt_template(config: dict[str, Any]) -> str | None
```

Return stripped `prompts.russian_word_forms` template, or `None` if missing.

<details>
<summary>Code:</summary>

```python
def get_russian_word_forms_prompt_template(config: dict[str, Any]) -> str | None:
    return get_prompt_template(config, PROMPT_KEY)
```

</details>

## 🔧 Function `parse_russian_word_forms`

```python
def parse_russian_word_forms(text: str, *, lemma: str = '') -> list[str]
```

Return unique word forms from an AI response, preserving first-seen order.

Lines may be bare words or bullet / numbered lists. The lemma is inserted
first when it is non-empty and missing from the response. Tokens without
Cyrillic letters are ignored, except the lemma itself.

<details>
<summary>Code:</summary>

````python
def parse_russian_word_forms(text: str, *, lemma: str = "") -> list[str]:
    forms: list[str] = []
    seen: set[str] = set()

    def add(candidate: str, *, allow_latin: bool = False) -> None:
        cleaned = candidate.strip().strip(".,;:!?\"'`«»()[]{}")
        if not cleaned or cleaned in seen:
            return
        if _WORD_TOKEN.fullmatch(cleaned) is None:
            return
        if not allow_latin and _HAS_CYRILLIC.search(cleaned) is None:
            return
        seen.add(cleaned)
        forms.append(cleaned)

    add(lemma, allow_latin=True)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines)

    for raw in cleaned.splitlines():
        line = _BULLET_PREFIX.sub("", raw).strip()
        if not line or line.startswith("#"):
            continue
        for part in re.split(r"[,;/|]+", line):
            token = part.strip()
            if not token:
                continue
            match = _WORD_TOKEN.search(token)
            if match is not None:
                add(match.group(0))
    return forms
````

</details>
