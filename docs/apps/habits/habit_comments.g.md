---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `habit_comments.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `HabitCommentsStore`](#%EF%B8%8F-class-habitcommentsstore)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `comment`](#%EF%B8%8F-method-comment)
  - [⚙️ Method `comments_for_habit`](#%EF%B8%8F-method-comments_for_habit)
  - [⚙️ Method `dates_with_comments`](#%EF%B8%8F-method-dates_with_comments)
  - [⚙️ Method `find_habit_file`](#%EF%B8%8F-method-find_habit_file)
  - [⚙️ Method `from_config (classmethod)`](#%EF%B8%8F-method-from_config-classmethod)
  - [⚙️ Method `is_configured`](#%EF%B8%8F-method-is_configured)
  - [⚙️ Method `root`](#%EF%B8%8F-method-root)
  - [⚙️ Method `set_comment`](#%EF%B8%8F-method-set_comment)
- [🏛️ Class `HabitDayComment`](#%EF%B8%8F-class-habitdaycomment)
- [🔧 Function `habit_comment_folder_slug`](#-function-habit_comment_folder_slug)
- [🔧 Function `parse_habit_comment_file`](#-function-parse_habit_comment_file)
- [🔧 Function `preview_habit_comment`](#-function-preview_habit_comment)
- [🔧 Function `render_habit_comment_file`](#-function-render_habit_comment_file)
- [🔧 Function `resolve_habit_comments_root`](#-function-resolve_habit_comments_root)

</details>

## 🏛️ Class `HabitCommentsStore`

```python
class HabitCommentsStore
```

Read and write per-habit daily comments as Markdown notes.

<details>
<summary>Code:</summary>

```python
class HabitCommentsStore:

    def __init__(
        self,
        root: Path | None,
        *,
        beginning: str = "",
        paths_git: list[str] | None = None,
        commit: bool = True,
    ) -> None:
        """Create a store rooted at the Notes-Habits folder.

        Args:

        - `root` (`Path | None`): Repository folder. `None` disables storage.
        - `beginning` (`str`): YAML front matter for new files.
        - `paths_git` (`list[str] | None`): Git roots used to resolve the repo.
        - `commit` (`bool`): Commit after a successful write. Defaults to `True`.

        """
        self._root = Path(root) if root is not None else None
        self._beginning = beginning or _DEFAULT_BEGINNING
        self._paths_git = list(paths_git or [])
        self._commit = commit

    def comment(self, habit_id: int, date_str: str) -> str:
        """Return the comment for `habit_id` on `date_str`, or `""`."""
        path = self.find_habit_file(habit_id)
        if path is None or not path.is_file():
            return ""
        for item in parse_habit_comment_file(path.read_text(encoding="utf-8")):
            if item.date == date_str:
                return item.text
        return ""

    def comments_for_habit(self, habit_id: int) -> list[HabitDayComment]:
        """Return all dated comments for a habit, newest first."""
        path = self.find_habit_file(habit_id)
        if path is None or not path.is_file():
            return []
        items = parse_habit_comment_file(path.read_text(encoding="utf-8"))
        return sorted(items, key=lambda item: item.date, reverse=True)

    def dates_with_comments(self, habit_ids: Iterable[int]) -> dict[int, set[str]]:
        """Return the comment dates present for each habit ID."""
        result: dict[int, set[str]] = {}
        for habit_id in habit_ids:
            result[int(habit_id)] = {item.date for item in self.comments_for_habit(int(habit_id))}
        return result

    def find_habit_file(self, habit_id: int) -> Path | None:
        """Return the existing Markdown file for `habit_id`, if any."""
        if self._root is None:
            return None
        prefix = f"{int(habit_id):04d}"
        if not self._root.is_dir():
            return None
        matches = sorted(path for path in self._root.glob(f"{prefix}-*") if path.is_dir())
        exact = self._root / prefix
        if exact.is_dir():
            matches = [exact, *matches]
        seen: set[Path] = set()
        for folder in matches:
            resolved = folder.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            named = folder / f"{folder.name}.md"
            if named.is_file():
                return named
            fallback = next(iter(sorted(folder.glob("*.md"))), None)
            if fallback is not None:
                return fallback
        return None

    @classmethod
    def from_config(cls, config: dict[str, Any] | None, *, commit: bool = True) -> HabitCommentsStore:
        """Build a store from application config."""
        data = config or {}
        paths_git = data.get("paths_git")
        git_roots = [str(path) for path in paths_git] if isinstance(paths_git, list) else []
        return cls(
            resolve_habit_comments_root(data),
            beginning=str(data.get("beginning_of_md") or _DEFAULT_BEGINNING),
            paths_git=git_roots,
            commit=commit,
        )

    def is_configured(self) -> bool:
        """Return whether a comments folder is configured."""
        return self._root is not None

    def root(self) -> Path | None:
        """Return the Notes-Habits folder, or `None` when unconfigured."""
        return self._root

    def set_comment(
        self,
        habit_id: int,
        date_str: str,
        text: str,
        *,
        habit_name: str,
    ) -> Path | None:
        """Write or delete the comment for one habit day.

        Empty `text` removes that date. Returns the Markdown path, or `None`
        when storage is not configured.

        """
        if self._root is None:
            return None
        cleaned = text.strip()
        path = self.find_habit_file(habit_id)
        if path is None and not cleaned:
            return None
        self._root.mkdir(parents=True, exist_ok=True)
        ensure_folder_git_repo(self._root)
        if self._root.as_posix() not in self._paths_git:
            self._paths_git.append(self._root.as_posix())

        if path is None:
            path = self._new_habit_file(habit_id, habit_name)
        existing = parse_habit_comment_file(path.read_text(encoding="utf-8")) if path.is_file() else []
        existed = any(item.date == date_str for item in existing)
        remaining = [item for item in existing if item.date != date_str]
        if cleaned:
            remaining.append(HabitDayComment(date=date_str, text=cleaned))
        previous = path.read_text(encoding="utf-8") if path.is_file() else ""
        rendered = render_habit_comment_file(
            remaining,
            habit_id=habit_id,
            habit_name=habit_name,
            beginning=self._beginning,
        )
        if rendered == previous:
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        if self._commit:
            self._commit_change(
                path,
                habit_name=habit_name,
                date_str=date_str,
                deleted=not cleaned,
                existed=existed,
            )
        return path

    def _commit_change(
        self,
        path: Path,
        *,
        habit_name: str,
        date_str: str,
        deleted: bool,
        existed: bool,
    ) -> None:
        repo = resolve_git_repo(path, self._paths_git)
        if repo is None:
            return
        if deleted:
            message = f"🗑️ Delete habit comment {habit_name} {date_str}"
        elif existed:
            message = f"🔧 Modify habit comment {habit_name} {date_str}"
        else:
            message = f"➕ Add habit comment {habit_name} {date_str}"  # noqa: RUF001
        ok, output = run_git_commit(repo, message, [path])
        if not ok:
            logger.warning("Habit comment git commit failed: %s", output)

    def _new_habit_file(self, habit_id: int, habit_name: str) -> Path:
        if self._root is None:
            msg = "Habit comments folder is not configured"
            raise RuntimeError(msg)
        folder_name = f"{int(habit_id):04d}-{habit_comment_folder_slug(habit_name)}"
        folder = self._root / folder_name
        return folder / f"{folder_name}.md"
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, root: Path | None, *, beginning: str = '', paths_git: list[str] | None = None, commit: bool = True) -> None
```

Create a store rooted at the Notes-Habits folder.

Args:

- [`root`](#%EF%B8%8F-method-root) (`Path | None`): Repository folder. `None` disables storage.
- `beginning` (`str`): YAML front matter for new files.
- `paths_git` (`list[str] | None`): Git roots used to resolve the repo.
- `commit` (`bool`): Commit after a successful write. Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        root: Path | None,
        *,
        beginning: str = "",
        paths_git: list[str] | None = None,
        commit: bool = True,
    ) -> None:
        self._root = Path(root) if root is not None else None
        self._beginning = beginning or _DEFAULT_BEGINNING
        self._paths_git = list(paths_git or [])
        self._commit = commit
```

</details>

### ⚙️ Method `comment`

```python
def comment(self, habit_id: int, date_str: str) -> str
```

Return the comment for [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id) on `date_str`, or `""`.

<details>
<summary>Code:</summary>

```python
def comment(self, habit_id: int, date_str: str) -> str:
        path = self.find_habit_file(habit_id)
        if path is None or not path.is_file():
            return ""
        for item in parse_habit_comment_file(path.read_text(encoding="utf-8")):
            if item.date == date_str:
                return item.text
        return ""
```

</details>

### ⚙️ Method `comments_for_habit`

```python
def comments_for_habit(self, habit_id: int) -> list[HabitDayComment]
```

Return all dated comments for a habit, newest first.

<details>
<summary>Code:</summary>

```python
def comments_for_habit(self, habit_id: int) -> list[HabitDayComment]:
        path = self.find_habit_file(habit_id)
        if path is None or not path.is_file():
            return []
        items = parse_habit_comment_file(path.read_text(encoding="utf-8"))
        return sorted(items, key=lambda item: item.date, reverse=True)
```

</details>

### ⚙️ Method `dates_with_comments`

```python
def dates_with_comments(self, habit_ids: Iterable[int]) -> dict[int, set[str]]
```

Return the comment dates present for each habit ID.

<details>
<summary>Code:</summary>

```python
def dates_with_comments(self, habit_ids: Iterable[int]) -> dict[int, set[str]]:
        result: dict[int, set[str]] = {}
        for habit_id in habit_ids:
            result[int(habit_id)] = {item.date for item in self.comments_for_habit(int(habit_id))}
        return result
```

</details>

### ⚙️ Method `find_habit_file`

```python
def find_habit_file(self, habit_id: int) -> Path | None
```

Return the existing Markdown file for [`habit_id`](dashboard_widgets.g.md#%EF%B8%8F-method-habit_id), if any.

<details>
<summary>Code:</summary>

```python
def find_habit_file(self, habit_id: int) -> Path | None:
        if self._root is None:
            return None
        prefix = f"{int(habit_id):04d}"
        if not self._root.is_dir():
            return None
        matches = sorted(path for path in self._root.glob(f"{prefix}-*") if path.is_dir())
        exact = self._root / prefix
        if exact.is_dir():
            matches = [exact, *matches]
        seen: set[Path] = set()
        for folder in matches:
            resolved = folder.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            named = folder / f"{folder.name}.md"
            if named.is_file():
                return named
            fallback = next(iter(sorted(folder.glob("*.md"))), None)
            if fallback is not None:
                return fallback
        return None
```

</details>

### ⚙️ Method `from_config (classmethod)`

```python
def from_config(cls, config: dict[str, Any] | None, *, commit: bool = True) -> HabitCommentsStore
```

Build a store from application config.

<details>
<summary>Code:</summary>

```python
def from_config(cls, config: dict[str, Any] | None, *, commit: bool = True) -> HabitCommentsStore:
        data = config or {}
        paths_git = data.get("paths_git")
        git_roots = [str(path) for path in paths_git] if isinstance(paths_git, list) else []
        return cls(
            resolve_habit_comments_root(data),
            beginning=str(data.get("beginning_of_md") or _DEFAULT_BEGINNING),
            paths_git=git_roots,
            commit=commit,
        )
```

</details>

### ⚙️ Method `is_configured`

```python
def is_configured(self) -> bool
```

Return whether a comments folder is configured.

<details>
<summary>Code:</summary>

```python
def is_configured(self) -> bool:
        return self._root is not None
```

</details>

### ⚙️ Method `root`

```python
def root(self) -> Path | None
```

Return the Notes-Habits folder, or `None` when unconfigured.

<details>
<summary>Code:</summary>

```python
def root(self) -> Path | None:
        return self._root
```

</details>

### ⚙️ Method `set_comment`

```python
def set_comment(self, habit_id: int, date_str: str, text: str, *, habit_name: str) -> Path | None
```

Write or delete the comment for one habit day.

Empty `text` removes that date. Returns the Markdown path, or `None`
when storage is not configured.

<details>
<summary>Code:</summary>

```python
def set_comment(
        self,
        habit_id: int,
        date_str: str,
        text: str,
        *,
        habit_name: str,
    ) -> Path | None:
        if self._root is None:
            return None
        cleaned = text.strip()
        path = self.find_habit_file(habit_id)
        if path is None and not cleaned:
            return None
        self._root.mkdir(parents=True, exist_ok=True)
        ensure_folder_git_repo(self._root)
        if self._root.as_posix() not in self._paths_git:
            self._paths_git.append(self._root.as_posix())

        if path is None:
            path = self._new_habit_file(habit_id, habit_name)
        existing = parse_habit_comment_file(path.read_text(encoding="utf-8")) if path.is_file() else []
        existed = any(item.date == date_str for item in existing)
        remaining = [item for item in existing if item.date != date_str]
        if cleaned:
            remaining.append(HabitDayComment(date=date_str, text=cleaned))
        previous = path.read_text(encoding="utf-8") if path.is_file() else ""
        rendered = render_habit_comment_file(
            remaining,
            habit_id=habit_id,
            habit_name=habit_name,
            beginning=self._beginning,
        )
        if rendered == previous:
            return path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        if self._commit:
            self._commit_change(
                path,
                habit_name=habit_name,
                date_str=date_str,
                deleted=not cleaned,
                existed=existed,
            )
        return path
```

</details>

## 🏛️ Class `HabitDayComment`

```python
class HabitDayComment
```

One dated comment for a habit.

<details>
<summary>Code:</summary>

```python
class HabitDayComment:

    date: str
    text: str
```

</details>

## 🔧 Function `habit_comment_folder_slug`

```python
def habit_comment_folder_slug(name: str) -> str
```

Return a filesystem-safe stem from a habit name.

<details>
<summary>Code:</summary>

```python
def habit_comment_folder_slug(name: str) -> str:
    cleaned = _UNSAFE_FOLDER_RE.sub("", (name or "").strip())
    cleaned = _WHITESPACE_RE.sub("-", cleaned).strip(".-")
    return cleaned or "habit"
```

</details>

## 🔧 Function `parse_habit_comment_file`

```python
def parse_habit_comment_file(content: str) -> list[HabitDayComment]
```

Return dated `## YYYY-MM-DD` sections from a habit comment file.

<details>
<summary>Code:</summary>

```python
def parse_habit_comment_file(content: str) -> list[HabitDayComment]:
    matches = list(_DATE_HEADING_RE.finditer(content))
    comments: list[HabitDayComment] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        text = content[start:end].strip()
        if text:
            comments.append(HabitDayComment(date=match.group(1), text=text))
    return comments
```

</details>

## 🔧 Function `preview_habit_comment`

```python
def preview_habit_comment(text: str) -> str
```

Return the first line of a comment, truncated for list rows.

<details>
<summary>Code:</summary>

```python
def preview_habit_comment(text: str) -> str:
    preview = text.splitlines()[0] if text else ""
    if len(preview) > _PREVIEW_MAX_LENGTH:
        return preview[: _PREVIEW_MAX_LENGTH - 1] + "…"
    return preview
```

</details>

## 🔧 Function `render_habit_comment_file`

```python
def render_habit_comment_file(comments: Iterable[HabitDayComment], *, habit_id: int, habit_name: str, beginning: str = '') -> str
```

Render a named-folder habit comment file, newest dates first.

<details>
<summary>Code:</summary>

```python
def render_habit_comment_file(
    comments: Iterable[HabitDayComment],
    *,
    habit_id: int,
    habit_name: str,
    beginning: str = "",
) -> str:
    ordered = sorted(
        (HabitDayComment(date=item.date, text=item.text.strip()) for item in comments if item.text.strip()),
        key=lambda item: item.date,
        reverse=True,
    )
    front = _frontmatter_with_habit_id(beginning or _DEFAULT_BEGINNING, habit_id).rstrip()
    lines = [front, "", f"# {habit_name.strip() or 'Habit'}", ""]
    for item in ordered:
        lines.extend([f"## {item.date}", "", item.text.rstrip(), ""])
    return "\n".join(lines).rstrip() + "\n"
```

</details>

## 🔧 Function `resolve_habit_comments_root`

```python
def resolve_habit_comments_root(config: dict[str, Any] | None) -> Path | None
```

Return the Notes-Habits repository path from config, if it can be inferred.

<details>
<summary>Code:</summary>

```python
def resolve_habit_comments_root(config: dict[str, Any] | None) -> Path | None:
    data = config or {}
    raw = str(data.get("path_habit_comments") or "").strip()
    if raw:
        return Path(raw)
    diary = str(data.get("path_diary") or "").strip()
    if diary:
        diary_path = Path(diary)
        if diary_path.name.lower() == "diary":
            return diary_path.parent.parent / "Notes-Habits"
        if diary_path.name == "Notes-Diaries":
            return diary_path.parent / "Notes-Habits"
    notes = str(data.get("path_notes") or "").strip()
    if notes:
        return Path(notes) / "Notes-Habits"
    return None
```

</details>
