---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `update_lucide_icons.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `LucideGitChanges`](#%EF%B8%8F-class-lucidegitchanges)
  - [⚙️ Method `has_changes (property)`](#%EF%B8%8F-method-has_changes-property)
  - [⚙️ Method `svg_names (property)`](#%EF%B8%8F-method-svg_names-property)
- [🏛️ Class `OnUpdateLucideIcons`](#%EF%B8%8F-class-onupdatelucideicons)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🔧 Function `commit_lucide_updates`](#-function-commit_lucide_updates)
- [🔧 Function `list_lucide_git_changes`](#-function-list_lucide_git_changes)

</details>

## 🏛️ Class `LucideGitChanges`

```python
class LucideGitChanges
```

SVG icon names changed under `assets/lucide` according to Git.

<details>
<summary>Code:</summary>

```python
class LucideGitChanges:

    added: tuple[str, ...] = ()
    modified: tuple[str, ...] = ()
    had_non_svg: bool = False

    @property
    def has_changes(self) -> bool:
        """Return whether Git reports any path under the Lucide folder."""
        return bool(self.added or self.modified or self.had_non_svg)

    @property
    def svg_names(self) -> tuple[str, ...]:
        """Return added then modified names without duplicates."""
        seen: set[str] = set()
        names: list[str] = []
        for name in (*self.added, *self.modified):
            if name in seen:
                continue
            seen.add(name)
            names.append(name)
        return tuple(names)
```

</details>

### ⚙️ Method `has_changes (property)`

```python
def has_changes(self) -> bool
```

Return whether Git reports any path under the Lucide folder.

<details>
<summary>Code:</summary>

```python
def has_changes(self) -> bool:
        return bool(self.added or self.modified or self.had_non_svg)
```

</details>

### ⚙️ Method `svg_names (property)`

```python
def svg_names(self) -> tuple[str, ...]
```

Return added then modified names without duplicates.

<details>
<summary>Code:</summary>

```python
def svg_names(self) -> tuple[str, ...]:
        seen: set[str] = set()
        names: list[str] = []
        for name in (*self.added, *self.modified):
            if name in seen:
                continue
            seen.add(name)
            names.append(name)
        return tuple(names)
```

</details>

## 🏛️ Class `OnUpdateLucideIcons`

```python
class OnUpdateLucideIcons(ActionBase)
```

Download the latest Lucide SVG set into `assets/lucide`.

Fetches `lucide-static` from npm, replaces local SVGs, optimizes them, and
updates `VERSION.txt` / `LICENSE.txt`. Commits the Lucide folder as
Update Lucide when Git reports changes, then shows thumbnails for added and
updated SVGs. Android `LucideIcons.kt` is not changed.

<details>
<summary>Code:</summary>

```python
class OnUpdateLucideIcons(ActionBase):

    icon = "⬇️"
    title = "Update Lucide icons"

    @ActionBase.handle_exceptions("update Lucide icons")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Start the Lucide sync on a background thread."""
        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)

    @ActionBase.handle_exceptions("update Lucide icons thread")
    def in_thread(self) -> LucideSyncResult:
        """Download and optimize Lucide SVGs."""

        def _progress(message: str) -> None:
            self.raise_if_work_cancelled()
            self.add_line(message)

        return sync_lucide_icons(progress=_progress)

    @ActionBase.handle_exceptions("update Lucide icons thread completion")
    def thread_after(self, result: Any) -> None:
        """Commit Lucide updates, show summary, and preview changed SVG thumbnails."""
        if not isinstance(result, LucideSyncResult):
            self.add_line(str(result))
            self.show_result()
            return
        clear_lucide_icon_caches()
        old = result.old_version or "(none)"
        new = result.new_version
        if old == new:
            summary = f"Lucide icons already at {new} ({result.svg_count} SVGs)."
        else:
            summary = f"Lucide icons updated: {old} → {new} ({result.svg_count} SVGs)."
        self.add_line(summary)
        self.add_line(f"Folder: {result.dest}")

        repo = get_project_root()
        changes = list_lucide_git_changes(repo, result.dest)
        if changes.has_changes:
            ok, detail = commit_lucide_updates(repo, result.dest)
            if ok:
                self.add_line(f"✅ {detail}")
            else:
                self.add_line(f"❌ {detail}")
        else:
            self.add_line("No Git changes under the Lucide folder.")

        self.show_toast(summary)
        sections, caption = self._thumbnail_sections(changes)
        self.show_result(lucide_sections=sections or None, lucide_caption=caption)

    def _thumbnail_sections(self, changes: LucideGitChanges) -> tuple[list[tuple[str, list[str]]], str]:
        """Return Lucide thumbnail sections and caption for the result dialog."""
        names = changes.svg_names
        if not names:
            return [], ""
        truncated = names[:_MAX_THUMBNAILS]
        sections: list[tuple[str, list[str]]] = []
        if changes.added:
            added = [name for name in truncated if name in set(changes.added)]
            if added:
                sections.append((f"Added ({len(changes.added)})", added))
        if changes.modified:
            modified = [name for name in truncated if name in set(changes.modified)]
            if modified:
                sections.append((f"Updated ({len(changes.modified)})", modified))
        if not sections:
            return [], ""
        note = ""
        if len(names) > _MAX_THUMBNAILS:
            note = f" Showing first {_MAX_THUMBNAILS} of {len(names)}."
        return sections, f"SVG icons added or updated according to Git.{note}"
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Start the Lucide sync on a background thread.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        self.start_thread(self.in_thread, self.thread_after, self.title, cancellable=True)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> LucideSyncResult
```

Download and optimize Lucide SVGs.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> LucideSyncResult:

        def _progress(message: str) -> None:
            self.raise_if_work_cancelled()
            self.add_line(message)

        return sync_lucide_icons(progress=_progress)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Commit Lucide updates, show summary, and preview changed SVG thumbnails.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        if not isinstance(result, LucideSyncResult):
            self.add_line(str(result))
            self.show_result()
            return
        clear_lucide_icon_caches()
        old = result.old_version or "(none)"
        new = result.new_version
        if old == new:
            summary = f"Lucide icons already at {new} ({result.svg_count} SVGs)."
        else:
            summary = f"Lucide icons updated: {old} → {new} ({result.svg_count} SVGs)."
        self.add_line(summary)
        self.add_line(f"Folder: {result.dest}")

        repo = get_project_root()
        changes = list_lucide_git_changes(repo, result.dest)
        if changes.has_changes:
            ok, detail = commit_lucide_updates(repo, result.dest)
            if ok:
                self.add_line(f"✅ {detail}")
            else:
                self.add_line(f"❌ {detail}")
        else:
            self.add_line("No Git changes under the Lucide folder.")

        self.show_toast(summary)
        sections, caption = self._thumbnail_sections(changes)
        self.show_result(lucide_sections=sections or None, lucide_caption=caption)
```

</details>

## 🔧 Function `commit_lucide_updates`

```python
def commit_lucide_updates(repo: Path, lucide_folder: Path, *, message: str = LUCIDE_COMMIT_MESSAGE) -> tuple[bool, str]
```

Stage the Lucide folder and create a commit when the index has changes.

<details>
<summary>Code:</summary>

```python
def commit_lucide_updates(
    repo: Path,
    lucide_folder: Path,
    *,
    message: str = LUCIDE_COMMIT_MESSAGE,
) -> tuple[bool, str]:
    try:
        rel = lucide_folder.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return False, f"Lucide folder is outside the repository: {lucide_folder}"

    add_p = git_run(repo, "add", "--", rel)
    if add_p.returncode != 0:
        return False, (add_p.stderr or add_p.stdout or "git add failed").strip()

    dirty = git_run(repo, "diff", "--cached", "--quiet")
    if dirty.returncode == 0:
        return True, "No Lucide changes to commit"

    commit_p = git_run(repo, "-c", "commit.gpgsign=false", "commit", "-m", message)
    if commit_p.returncode != 0:
        return False, (commit_p.stderr or commit_p.stdout or "git commit failed").strip()
    return True, f"Committed `{message}`"
```

</details>

## 🔧 Function `list_lucide_git_changes`

```python
def list_lucide_git_changes(repo: Path, lucide_folder: Path) -> LucideGitChanges
```

Return added and modified Lucide SVG names from `git status --porcelain`.

<details>
<summary>Code:</summary>

```python
def list_lucide_git_changes(repo: Path, lucide_folder: Path) -> LucideGitChanges:
    try:
        rel = lucide_folder.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return LucideGitChanges()

    proc = git_run(repo, "status", "--porcelain", "-u", "--", rel)
    if proc.returncode != 0 or not proc.stdout.strip():
        return LucideGitChanges()

    added: list[str] = []
    modified: list[str] = []
    had_non_svg = False
    for changed in parse_porcelain_files(proc.stdout):
        path = changed.path.replace("\\", "/")
        name = Path(path).name
        if not name.endswith(".svg"):
            had_non_svg = True
            continue
        stem = name[: -len(".svg")]
        kind = _change_kind(changed.status)
        if kind == "added":
            added.append(stem)
        elif kind == "modified":
            modified.append(stem)
        elif kind == "deleted":
            had_non_svg = True
    added_sorted = tuple(sorted(dict.fromkeys(added)))
    modified_sorted = tuple(sorted(dict.fromkeys(modified)))
    return LucideGitChanges(added_sorted, modified_sorted, had_non_svg=had_non_svg)
```

</details>
