---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `rules.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `RuleWarning`](#%EF%B8%8F-class-rulewarning)
- [🔧 Function `apply_rules`](#-function-apply_rules)
- [🔧 Function `expand_rule_placeholders`](#-function-expand_rule_placeholders)
- [🔧 Function `matching_playlist_names`](#-function-matching_playlist_names)

</details>

## 🏛️ Class `RuleWarning`

```python
class RuleWarning
```

A skipped or incomplete rule application.

<details>
<summary>Code:</summary>

```python
class RuleWarning:

    message: str
```

</details>

## 🔧 Function `apply_rules`

```python
def apply_rules(playlists: dict[str, list[str]], rules: list[dict[str, Any]], *, placeholders: dict[str, str], file_index: FileIndex) -> list[RuleWarning]
```

Apply `rules` in order, mutating `playlists` (name → tracks).

<details>
<summary>Code:</summary>

```python
def apply_rules(
    playlists: dict[str, list[str]],
    rules: list[dict[str, Any]],
    *,
    placeholders: dict[str, str],
    file_index: FileIndex,
) -> list[RuleWarning]:
    warnings: list[RuleWarning] = []
    for raw in rules:
        if not isinstance(raw, dict):
            warnings.append(RuleWarning("Skipped a non-object rule"))
            continue
        rule = expand_rule_placeholders(raw, placeholders)
        kind = str(rule.get("type") or "").strip()
        if kind not in KNOWN_RULE_TYPES:
            warnings.append(RuleWarning(f"Unknown rule type: {kind or '(empty)'}"))
            continue
        if kind == "restrict_folder":
            warnings.extend(_restrict_folder(playlists, rule))
        elif kind == "ensure_subset":
            warnings.extend(_ensure_subset(playlists, rule))
        elif kind == "union":
            warnings.extend(_union(playlists, rule))
        else:
            warnings.extend(_rebuild_remainder(playlists, rule, file_index))
    return warnings
```

</details>

## 🔧 Function `expand_rule_placeholders`

```python
def expand_rule_placeholders(rule: dict[str, Any], values: dict[str, str]) -> dict[str, Any]
```

Replace `{music_root}` / `{stream_root}` in string fields of `rule`.

<details>
<summary>Code:</summary>

```python
def expand_rule_placeholders(rule: dict[str, Any], values: dict[str, str]) -> dict[str, Any]:
    expanded: dict[str, Any] = {}
    for key, value in rule.items():
        if isinstance(value, str):
            expanded[key] = value.format_map(values)
        elif isinstance(value, list):
            expanded[key] = [item.format_map(values) if isinstance(item, str) else item for item in value]
        else:
            expanded[key] = value
    return expanded
```

</details>

## 🔧 Function `matching_playlist_names`

```python
def matching_playlist_names(names: list[str], pattern: str) -> list[str]
```

Return playlist names matching a glob `pattern`.

<details>
<summary>Code:</summary>

```python
def matching_playlist_names(names: list[str], pattern: str) -> list[str]:
    return [name for name in names if fnmatch.fnmatch(name, pattern)]
```

</details>
