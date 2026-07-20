---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `node_update.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnNodeUpdate`](#️-class-onnodeupdate)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnNodeUpdate`

```python
class OnNodeUpdate(ActionBase)
```

Update `Node.js` to the latest version via winget.

This action upgrades OpenJS.NodeJS using the Windows Package Manager (winget)
command `winget upgrade OpenJS.NodeJS`. Available only on Windows.

<details>
<summary>Code:</summary>

```python
class OnNodeUpdate(ActionBase):

    icon = "📥"
    title = "Update Node.js"

    @ActionBase.handle_exceptions("Node.js update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update `Node.js` to the latest version via winget."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("Node.js update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        # Avoid interactive agreement prompts (msstore) by pinning the "winget" source
        # and disabling interactivity.
        cmd = (
            "winget upgrade -e --id OpenJS.NodeJS.LTS --source winget "
            "--accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
        )
        return h.dev.run_command(cmd)

    @ActionBase.handle_exceptions("Node.js update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("Node.js update completed")
        self.add_line(result)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Update `Node.js` to the latest version via winget.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows (winget).")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Execute code in a separate thread. For performing long-running operations.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        # Avoid interactive agreement prompts (msstore) by pinning the "winget" source
        # and disabling interactivity.
        cmd = (
            "winget upgrade -e --id OpenJS.NodeJS.LTS --source winget "
            "--accept-package-agreements --accept-source-agreements --silent --disable-interactivity"
        )
        return h.dev.run_command(cmd)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Execute code in the main thread after in_thread(). For handling the results of thread execution.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:
        self.show_toast("Node.js update completed")
        self.add_line(result)
        self.show_result()
```

</details>
