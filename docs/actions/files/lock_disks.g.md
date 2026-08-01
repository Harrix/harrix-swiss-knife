---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `lock_disks.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnLockDisks`](#%EF%B8%8F-class-onlockdisks)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnLockDisks`

```python
class OnLockDisks(ActionBase)
```

Lock BitLocker-encrypted drives.

This action locks all drives specified in the configuration's `block_drives` list
using BitLocker encryption, forcibly dismounting them if necessary to ensure
secure protection of the drive contents.

<details>
<summary>Code:</summary>

```python
class OnLockDisks(ActionBase):

    icon = "🔒"
    title = "Lock disks (BitLocker)"

    @ActionBase.handle_exceptions("locking disks")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Lock BitLocker-encrypted drives."""
        drives = self.config.get("block_drives") or []
        if not drives:
            self.add_line('❌ config "block_drives" is missing or empty.')
            self.show_result()
            return
        self._drives = list(drives)
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("locking disks thread")
    def in_thread(self) -> None:
        """Run BitLocker lock commands as admin in a worker thread."""
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in self._drives])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)

    @ActionBase.handle_exceptions("locking disks completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show result dialog after disk lock finishes."""
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Lock BitLocker-encrypted drives.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        drives = self.config.get("block_drives") or []
        if not drives:
            self.add_line('❌ config "block_drives" is missing or empty.')
            self.show_result()
            return
        self._drives = list(drives)
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> None
```

Run BitLocker lock commands as admin in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        commands = "\n".join([f"manage-bde -lock {drive}: -ForceDismount" for drive in self._drives])
        result = h.dev.run_powershell_script_as_admin(commands)
        self.add_line(result)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show result dialog after disk lock finishes.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_result()
```

</details>
