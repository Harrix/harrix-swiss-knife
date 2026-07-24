---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_suggest.py`

## 🔧 Function `suggest_categories`

```python
def suggest_categories(description: str, history_pairs: list[tuple[str, str]], category_names: list[str]) -> list[str]
```

Return up to `limit` category names suggested for `description`.

Prefers matches from past `(description, category)` pairs, then fills remaining
slots by fuzzy-matching against category names. History wins ties.

<details>
<summary>Code:</summary>

```python
def suggest_categories(
    description: str,
    history_pairs: list[tuple[str, str]],
    category_names: list[str],
    *,
    limit: int = _DEFAULT_LIMIT,
    min_score: float = _DEFAULT_MIN_SCORE,
    min_length: int = _DEFAULT_MIN_LENGTH,
) -> list[str]:
    query = description.strip().lower()
    if len(query) < min_length:
        return []

    scores: dict[str, tuple[float, int]] = {}

    for past_description, category_name in history_pairs:
        if not category_name:
            continue
        score = _score_texts(query, past_description.strip().lower())
        if score < min_score:
            continue
        _keep_best(scores, category_name, score, priority=0)

    for category_name in category_names:
        if not category_name:
            continue
        score = _score_texts(query, category_name.strip().lower())
        if score < min_score:
            continue
        _keep_best(scores, category_name, score, priority=1)

    ranked = sorted(scores.items(), key=lambda item: (-item[1][0], item[1][1], item[0].lower()))
    return [name for name, _ in ranked[:limit]]
```

</details>
