---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `upgrade_uv_python.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnUpgradeUvPython`](#%EF%B8%8F-class-onupgradeuvpython)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnUpgradeUvPython`

```python
class OnUpgradeUvPython(ActionBase)
```

Upgrade uv-managed Python versions to the latest patch.

Runs `uv python upgrade` for every CPython installed via uv.

<details>
<summary>Code:</summary>

```python
class OnUpgradeUvPython(ActionBase):

    icon = "📥"
    title = "Upgrade uv Python"

    @ActionBase.handle_exceptions("uv python upgrade")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Run `uv python upgrade`."""
        if shutil.which("uv") is None:
            self.add_line("❌ uv not found on PATH. Install uv first: https://docs.astral.sh/uv/")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv python upgrade thread")
    def in_thread(self) -> str | None:
        """Execute `uv python upgrade` in a worker thread."""
        return h.dev.run_command(["uv", "python", "upgrade"])

    @ActionBase.handle_exceptions("uv python upgrade thread completion")
    def thread_after(self, result: Any) -> None:
        """Show toast and the upgrade log."""
        self.show_toast(f"{self.title} completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Run `uv python upgrade`.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if shutil.which("uv") is None:
            self.add_line("❌ uv not found on PATH. Install uv first: https://docs.astral.sh/uv/")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute `uv python upgrade` in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        return h.dev.run_command(["uv", "python", "upgrade"])
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and the upgrade log.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast(f"{self.title} completed")
        self.add_line(result)
        self.show_result()
```

</details>
