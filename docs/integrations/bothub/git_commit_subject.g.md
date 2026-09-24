---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `git_commit_subject.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_git_commit_subject_prompt`](#-function-build_git_commit_subject_prompt)
- [🔧 Function `normalize_commit_subject`](#-function-normalize_commit_subject)

</details>

## 🔧 Function `build_git_commit_subject_prompt`

```python
def build_git_commit_subject_prompt(description: str, config: dict[str, Any]) -> str
```

Build the commit-subject prompt for `description`.

Raises:

- `ValueError`: If the prompt template or API key is not configured.

<details>
<summary>Code:</summary>

```python
def build_git_commit_subject_prompt(description: str, config: dict[str, Any]) -> str:
    return build_prompt(
        config,
        PROMPT_KEY,
        {"TEXT": description},
        prompt_display_name=PROMPT_KEY,
    )
```

</details>

## 🔧 Function `normalize_commit_subject`

```python
def normalize_commit_subject(text: str) -> str
```

Return the first subject line, without fences, quotes, or a trailing period.

<details>
<summary>Code:</summary>

````python
def normalize_commit_subject(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = [line for line in cleaned.splitlines() if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()
    subject = next((line.strip() for line in cleaned.splitlines() if line.strip()), "")
    if len(subject) >= _MIN_WRAPPED_SUBJECT_LEN and subject[0] == subject[-1] and subject[0] in {'"', "'"}:
        subject = subject[1:-1].strip()
    if subject.endswith(".") and not subject.endswith(".."):
        subject = subject[:-1].rstrip()
    return subject
````

</details>
