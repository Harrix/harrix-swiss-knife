---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `move_md_into_named_folders.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnMoveMdIntoNamedFolders`](#%EF%B8%8F-class-onmovemdintonamedfolders)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)
- [🏛️ Class `_MoveItem`](#%EF%B8%8F-class-_moveitem)
- [🔧 Function `_is_g_md`](#-function-_is_g_md)
- [🔧 Function `_scan_folder`](#-function-_scan_folder)

</details>

## 🏛️ Class `OnMoveMdIntoNamedFolders`

```python
class OnMoveMdIntoNamedFolders(ActionBase)
```

Move Markdown notes into same-named subfolders (one note — one folder).

Notes already in the correct layout (e.g. `Python/Python.md`) are left unchanged.
Flat notes (e.g. `Math/Numbers.md`) are moved to `Math/Numbers/Numbers.md`.
Files with the `.g.md` extension are skipped.

<details>
<summary>Code:</summary>

```python
class OnMoveMdIntoNamedFolders(ActionBase):

    icon = "📁"
    title = "Move MD into named folders in …"

    @ActionBase.handle_exceptions("moving markdown into named folders")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Move Markdown notes into same-named subfolders recursively."""
        doc = inspect.getdoc(type(self))
        if doc:
            self.show_instructions(doc, title=self.title)

        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        folder = Path(self.folder_path).resolve()
        to_move, conflicts, already_ok_count, g_md_count = _scan_folder(folder)

        self._moves: list[_MoveItem] = [_MoveItem(source, target, overwrite=False) for source, target in to_move]
        skipped_conflicts = 0

        for source, target in conflicts:
            if self.get_yes_no_question(
                "File already exists",
                f"Target already exists:\n{target}\n\nOverwrite with:\n{source}?",
                default_yes=False,
            ):
                self._moves.append(_MoveItem(source, target, overwrite=True))
            else:
                skipped_conflicts += 1
                self.add_line(f"⏭️ Skipped (conflict): {source.relative_to(folder)}")

        self._scan_stats = (already_ok_count, g_md_count, skipped_conflicts)
        self.add_line(f"🔵 Folder: {folder}")
        self.add_line(f"🔢 Already in named folders: {already_ok_count}")
        self.add_line(f"🔢 Skipped .g.md files: {g_md_count}")
        if skipped_conflicts:
            self.add_line(f"🔢 Skipped conflicts: {skipped_conflicts}")

        if not self._moves:
            self.add_line("✅ Nothing to move.")
            self.show_result()
            return

        self.add_line(f"🔢 To move: {len(self._moves)}")
        self._move_stats = (0, 0)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("moving markdown into named folders thread")
    def in_thread(self) -> str | None:
        """Execute file moves in a separate thread."""
        if self.folder_path is None:
            return
        folder = Path(self.folder_path).resolve()
        moved_count = 0
        error_count = 0

        for item in self._moves:
            rel_source = item.source.relative_to(folder)
            rel_target = item.target.relative_to(folder)
            try:
                item.target.parent.mkdir(parents=True, exist_ok=True)
                if item.overwrite and item.target.exists():
                    item.target.unlink()
                item.source.rename(item.target)
                self.add_line(f"✅ Moved: {rel_source} → {rel_target}")
                moved_count += 1
            except OSError as e:
                self.add_line(f"❌ Failed: {rel_source} → {rel_target}: {e}")
                error_count += 1

        self._move_stats = (moved_count, error_count)

    @ActionBase.handle_exceptions("moving markdown into named folders thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result after thread completes."""
        moved_count, error_count = self._move_stats
        already_ok_count, g_md_count, skipped_conflicts = self._scan_stats
        self.add_line(f"\n🔢 Moved: {moved_count}")
        if error_count:
            self.add_line(f"🔢 Errors: {error_count}")
        self.add_line(f"🔢 Already OK: {already_ok_count}")
        self.add_line(f"🔢 Skipped .g.md: {g_md_count}")
        if skipped_conflicts:
            self.add_line(f"🔢 Skipped conflicts: {skipped_conflicts}")

        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Move Markdown notes into same-named subfolders recursively.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        doc = inspect.getdoc(type(self))
        if doc:
            self.show_instructions(doc, title=self.title)

        self.folder_path = self.dialogs.get_folder_with_choice_option(
            self.config["paths_notes"], self.config["path_notes"]
        )
        if not self.folder_path:
            return

        folder = Path(self.folder_path).resolve()
        to_move, conflicts, already_ok_count, g_md_count = _scan_folder(folder)

        self._moves: list[_MoveItem] = [_MoveItem(source, target, overwrite=False) for source, target in to_move]
        skipped_conflicts = 0

        for source, target in conflicts:
            if self.get_yes_no_question(
                "File already exists",
                f"Target already exists:\n{target}\n\nOverwrite with:\n{source}?",
                default_yes=False,
            ):
                self._moves.append(_MoveItem(source, target, overwrite=True))
            else:
                skipped_conflicts += 1
                self.add_line(f"⏭️ Skipped (conflict): {source.relative_to(folder)}")

        self._scan_stats = (already_ok_count, g_md_count, skipped_conflicts)
        self.add_line(f"🔵 Folder: {folder}")
        self.add_line(f"🔢 Already in named folders: {already_ok_count}")
        self.add_line(f"🔢 Skipped .g.md files: {g_md_count}")
        if skipped_conflicts:
            self.add_line(f"🔢 Skipped conflicts: {skipped_conflicts}")

        if not self._moves:
            self.add_line("✅ Nothing to move.")
            self.show_result()
            return

        self.add_line(f"🔢 To move: {len(self._moves)}")
        self._move_stats = (0, 0)
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute file moves in a separate thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        if self.folder_path is None:
            return
        folder = Path(self.folder_path).resolve()
        moved_count = 0
        error_count = 0

        for item in self._moves:
            rel_source = item.source.relative_to(folder)
            rel_target = item.target.relative_to(folder)
            try:
                item.target.parent.mkdir(parents=True, exist_ok=True)
                if item.overwrite and item.target.exists():
                    item.target.unlink()
                item.source.rename(item.target)
                self.add_line(f"✅ Moved: {rel_source} → {rel_target}")
                moved_count += 1
            except OSError as e:
                self.add_line(f"❌ Failed: {rel_source} → {rel_target}: {e}")
                error_count += 1

        self._move_stats = (moved_count, error_count)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result after thread completes.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        moved_count, error_count = self._move_stats
        already_ok_count, g_md_count, skipped_conflicts = self._scan_stats
        self.add_line(f"\n🔢 Moved: {moved_count}")
        if error_count:
            self.add_line(f"🔢 Errors: {error_count}")
        self.add_line(f"🔢 Already OK: {already_ok_count}")
        self.add_line(f"🔢 Skipped .g.md: {g_md_count}")
        if skipped_conflicts:
            self.add_line(f"🔢 Skipped conflicts: {skipped_conflicts}")

        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

## 🏛️ Class `_MoveItem`

```python
class _MoveItem
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
class _MoveItem:
    source: Path
    target: Path
    overwrite: bool
```

</details>

## 🔧 Function `_is_g_md`

```python
def _is_g_md(path: Path) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _is_g_md(path: Path) -> bool:
    return path.name.endswith(".g.md")
```

</details>

## 🔧 Function `_scan_folder`

```python
def _scan_folder(folder: Path) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]], int, int]
```

Return `(to_move, conflicts, already_ok_count, g_md_count)`.

<details>
<summary>Code:</summary>

```python
def _scan_folder(
    folder: Path,
) -> tuple[list[tuple[Path, Path]], list[tuple[Path, Path]], int, int]:
    to_move: list[tuple[Path, Path]] = []
    conflicts: list[tuple[Path, Path]] = []
    already_ok_count = 0
    g_md_count = 0

    for md_path in sorted(folder.rglob("*.md")):
        if _is_g_md(md_path):
            g_md_count += 1
            continue
        if h.md.is_note_in_named_folder(md_path):
            already_ok_count += 1
            continue

        target = h.md.named_note_md_path(md_path.parent, md_path.stem)
        if target.exists() and target.resolve() != md_path.resolve():
            conflicts.append((md_path, target))
        else:
            to_move.append((md_path, target))

    return to_move, conflicts, already_ok_count, g_md_count
```

</details>
