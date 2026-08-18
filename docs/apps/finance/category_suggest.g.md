---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `category_suggest.py`

## 🔧 Function `suggest_categories`

```python
def suggest_categories(description: str, history_pairs: Sequence[tuple[str, str, int]], category_names: Sequence[str], *, category_aliases: Mapping[str, Sequence[str]] | None = None, limit: int = _DEFAULT_LIMIT, min_score: float = _DEFAULT_MIN_SCORE, min_length: int = _DEFAULT_MIN_LENGTH) -> list[str]
```

Return up to `limit` category names suggested for `description`.

Prefers close matches to past descriptions (weighted by how often that pair
was used), then category English/local names. Token prefix and typo-tolerant
matches are used instead of loose full-string fuzzy matching.

<details>
<summary>Code:</summary>

```python
def suggest_categories(
    description: str,
    history_pairs: Sequence[tuple[str, str, int]],
    category_names: Sequence[str],
    *,
    category_aliases: Mapping[str, Sequence[str]] | None = None,
    limit: int = _DEFAULT_LIMIT,
    min_score: float = _DEFAULT_MIN_SCORE,
    min_length: int = _DEFAULT_MIN_LENGTH,
) -> list[str]:
    query = description.strip().lower()
    if len(query) < min_length:
        return []

    allowed = {name for name in category_names if name}
    if not allowed:
        return []

    scores: dict[str, float] = {}
    history_counts: dict[str, int] = {}

    for row in history_pairs:
        category_name = row[1]
        if not category_name or category_name not in allowed:
            continue
        past = str(row[0]).strip().lower()
        count = max(int(row[2]), 1)
        score = _score_texts(query, past)
        if score < min_score:
            continue
        previous = scores.get(category_name, 0.0)
        if score > previous:
            scores[category_name] = score
        history_counts[category_name] = history_counts.get(category_name, 0) + max(count, 1)

    for category_name in allowed:
        aliases = [category_name]
        if category_aliases is not None:
            aliases.extend(category_aliases.get(category_name, ()))
        best_alias = 0.0
        for alias in aliases:
            text = str(alias).strip().lower()
            if not text:
                continue
            best_alias = max(best_alias, _score_texts(query, text))
        if best_alias < min_score:
            continue
        previous = scores.get(category_name, 0.0)
        if best_alias > previous:
            scores[category_name] = best_alias

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            -(item[1] + _FREQUENCY_BONUS * math.log10(1 + history_counts.get(item[0], 0))),
            item[0].lower(),
        ),
    )
    return [name for name, _ in ranked[:limit]]
```

</details>
