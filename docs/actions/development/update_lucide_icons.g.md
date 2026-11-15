---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `update_lucide_icons.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnUpdateLucideIcons`](#%EF%B8%8F-class-onupdatelucideicons)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnUpdateLucideIcons`

```python
class OnUpdateLucideIcons(ActionBase)
```

Download the latest Lucide SVG set into `assets/lucide`.

Fetches `lucide-static` from npm, replaces local SVGs, optimizes them, and
updates `VERSION.txt` / `LICENSE.txt`. Android `LucideIcons.kt` is not changed.

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
        """Show sync summary and clear in-process Lucide caches."""
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
        self.show_toast(summary)
        self.show_result()
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

Show sync summary and clear in-process Lucide caches.

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
        self.show_toast(summary)
        self.show_result()
```

</details>
