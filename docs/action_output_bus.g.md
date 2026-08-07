---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `action_output_bus.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ActionOutputBus`](#%EF%B8%8F-class-actionoutputbus)
  - [⚙️ Method `append_line`](#%EF%B8%8F-method-append_line)
  - [⚙️ Method `set_active_output`](#%EF%B8%8F-method-set_active_output)

</details>

## 🏛️ Class `ActionOutputBus`

```python
class ActionOutputBus(QObject)
```

Thread-safe bus for action output events (via queued Qt signals).

<details>
<summary>Code:</summary>

```python
class ActionOutputBus(QObject):

    active_output_changed: Signal = Signal(str)  # absolute path as string
    line_appended: Signal = Signal(str, str)  # (absolute path, line)

    def append_line(self, path: Path, line: str) -> None:
        """Emit a single output line for `path`."""
        self.line_appended.emit(str(path.resolve()), line)

    def set_active_output(self, path: Path) -> None:
        """Set currently active output `path`."""
        self.active_output_changed.emit(str(path.resolve()))
```

</details>

### ⚙️ Method `append_line`

```python
def append_line(self, path: Path, line: str) -> None
```

Emit a single output line for `path`.

<details>
<summary>Code:</summary>

```python
def append_line(self, path: Path, line: str) -> None:
        self.line_appended.emit(str(path.resolve()), line)
```

</details>

### ⚙️ Method `set_active_output`

```python
def set_active_output(self, path: Path) -> None
```

Set currently active output `path`.

<details>
<summary>Code:</summary>

```python
def set_active_output(self, path: Path) -> None:
        self.active_output_changed.emit(str(path.resolve()))
```

</details>
