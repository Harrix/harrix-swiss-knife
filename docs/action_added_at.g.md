---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_added_at.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `added_at_for`](#-function-added_at_for)
- [🔧 Function `first_added_at_from_git`](#-function-first_added_at_from_git)
- [🔧 Function `format_added_at_date`](#-function-format_added_at_date)
- [🔧 Function `generate_action_added_at`](#-function-generate_action_added_at)
- [🔧 Function `load_action_added_at`](#-function-load_action_added_at)
- [🔧 Function `sort_items_newest_first`](#-function-sort_items_newest_first)
- [🔧 Function `write_action_added_at`](#-function-write_action_added_at)

</details>

## 🔧 Function `added_at_for`

```python
def added_at_for(class_name: str, *, path: Path | None = None) -> datetime | None
```

Return the parsed added-at stamp for `class_name`, or `None` if unknown.

<details>
<summary>Code:</summary>

```python
def added_at_for(class_name: str, *, path: Path | None = None) -> datetime | None:
    stamp = load_action_added_at(path).get(class_name, "")
    if not stamp:
        return None
    try:
        parsed = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed
```

</details>

## 🔧 Function `first_added_at_from_git`

```python
def first_added_at_from_git(class_name: str, *, repo: Path) -> str | None
```

Return the first author ISO date when `class On…` appeared in Python sources.

<details>
<summary>Code:</summary>

```python
def first_added_at_from_git(class_name: str, *, repo: Path) -> str | None:
    if not class_name:
        return None
    try:
        completed = subprocess.run(
            ["git", "log", "-S", f"class {class_name}", "--format=%aI", "--reverse", "--", "*.py"],  # noqa: S607
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        logger.exception("Failed to run git log for %s", class_name)
        return None
    if completed.returncode != 0:
        logger.warning(
            "git log failed for %s (exit %s): %s",
            class_name,
            completed.returncode,
            (completed.stderr or "").strip(),
        )
        return None
    for line in completed.stdout.splitlines():
        stamp = line.strip()
        if stamp:
            return stamp
    return None
```

</details>

## 🔧 Function `format_added_at_date`

```python
def format_added_at_date(stamp: datetime | None) -> str
```

Return `YYYY-MM-DD` for a stamp, or an empty string.

<details>
<summary>Code:</summary>

```python
def format_added_at_date(stamp: datetime | None) -> str:
    if stamp is None:
        return ""
    return stamp.date().isoformat()
```

</details>

## 🔧 Function `generate_action_added_at`

```python
def generate_action_added_at(class_names: Sequence[str], *, path: Path | None = None, repo: Path | None = None, force: bool = False) -> ActionAddedAtMap
```

Merge Git first-appearance dates into `action_added_at.json`.

Existing keys are kept unless `force` is true. Missing class names are
resolved with `git log -S "class On…"`. If Git has no hit (for example an
uncommitted new action), the current local timestamp is stored instead.

<details>
<summary>Code:</summary>

```python
def generate_action_added_at(
    class_names: Sequence[str],
    *,
    path: Path | None = None,
    repo: Path | None = None,
    force: bool = False,
) -> ActionAddedAtMap:
    out_path = path if path is not None else get_action_added_at_path()
    repo_root = repo if repo is not None else get_project_root()
    existing = load_action_added_at(out_path)
    result: ActionAddedAtMap = dict(existing)
    unique_names = sorted({name for name in class_names if name})
    for class_name in unique_names:
        if not force and class_name in result and result[class_name]:
            continue
        stamp = first_added_at_from_git(class_name, repo=repo_root)
        if not stamp:
            # Uncommitted / new actions: use local now so Newest sorting works.
            stamp = datetime.now().astimezone().isoformat(timespec="seconds")
            logger.warning("No Git added-at for %s; using now %s", class_name, stamp)
        result[class_name] = stamp
        logger.info("%s → %s", class_name, stamp)
    write_action_added_at(result, path=out_path)
    return result
```

</details>

## 🔧 Function `load_action_added_at`

```python
def load_action_added_at(path: Path | None = None) -> ActionAddedAtMap
```

Load added-at map from JSON; return empty dict if missing or invalid.

<details>
<summary>Code:</summary>

```python
def load_action_added_at(path: Path | None = None) -> ActionAddedAtMap:
    added_path = path if path is not None else get_action_added_at_path()
    if not added_path.is_file():
        return {}
    try:
        raw = json.loads(added_path.read_text(encoding="utf8"))
    except (OSError, json.JSONDecodeError):
        logger.exception("Failed to load action added-at from %s", added_path)
        return {}
    if not isinstance(raw, dict):
        return {}
    result: ActionAddedAtMap = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, str) and value.strip():
            result[key] = value.strip()
    return result
```

</details>

## 🔧 Function `sort_items_newest_first`

```python
def sort_items_newest_first(items: Sequence[_T], *, class_name_of: Callable[[_T], str], path: Path | None = None) -> list[_T]
```

Return `items` ordered by added-at descending; unknown dates last.

Equal dates keep a stable alphabetical order by class name.

<details>
<summary>Code:</summary>

```python
def sort_items_newest_first(
    items: Sequence[_T],
    *,
    class_name_of: Callable[[_T], str],
    path: Path | None = None,
) -> list[_T]:
    mapping = load_action_added_at(path)
    ranked: list[tuple[datetime, str, int, _T]] = []
    for index, item in enumerate(items):
        class_name = class_name_of(item)
        stamp = mapping.get(class_name, "")
        ranked.append((_parse_added_at(stamp), class_name, index, item))
    ranked.sort(key=lambda row: row[2])
    ranked.sort(key=lambda row: row[1])
    ranked.sort(key=lambda row: row[0], reverse=True)
    return [row[3] for row in ranked]
```

</details>

## 🔧 Function `write_action_added_at`

```python
def write_action_added_at(data: ActionAddedAtMap, *, path: Path | None = None) -> None
```

Write the added-at map as pretty JSON with sorted keys.

<details>
<summary>Code:</summary>

```python
def write_action_added_at(data: ActionAddedAtMap, *, path: Path | None = None) -> None:
    out_path = path if path is not None else get_action_added_at_path()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    ordered = {key: data[key] for key in sorted(data)}
    payload = json.dumps(ordered, ensure_ascii=False, indent=2) + "\n"
    out_path.write_text(payload, encoding="utf8")
```

</details>
