---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `log.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OutcomeLog`](#%EF%B8%8F-class-outcomelog)
  - [⚙️ Method `add`](#%EF%B8%8F-method-add)
  - [⚙️ Method `detail`](#%EF%B8%8F-method-detail)
  - [⚙️ Method `line`](#%EF%B8%8F-method-line)
  - [⚙️ Method `set_log`](#%EF%B8%8F-method-set_log)
  - [⚙️ Method `step`](#%EF%B8%8F-method-step)
  - [⚙️ Method `summary_lines`](#%EF%B8%8F-method-summary_lines)

</details>

## 🏛️ Class `OutcomeLog`

```python
class OutcomeLog
```

Collect install/skip/already/failed messages like the PowerShell installer.

<details>
<summary>Code:</summary>

```python
class OutcomeLog:

    installed: list[str] = field(default_factory=list)
    already: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    _log: LogFn | None = None
    _file: Path | None = None

    def add(self, category: str, message: str) -> None:
        """Record a categorized outcome and emit a log line."""
        bucket = {
            "installed": self.installed,
            "already": self.already,
            "skipped": self.skipped,
            "failed": self.failed,
        }.get(category)
        if bucket is not None:
            bucket.append(message)
        prefix = {"installed": "✅", "already": "i", "skipped": "⚠️", "failed": "❌"}.get(category, "•")
        self.line(f"{prefix} {message}")

    def detail(self, message: str) -> None:
        """Emit an indented detail line."""
        self.line(f"    {message}")

    def line(self, message: str) -> None:
        """Write a line to the callback and optional log file."""
        if self._log is not None:
            self._log(message)
        if self._file is not None:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            with self._file.open("a", encoding="utf-8") as f:
                f.write(message + "\n")

    def set_log(self, log: LogFn | None, *, log_file: Path | None = None) -> None:
        """Attach a live log callback and optional log file path."""
        self._log = log
        self._file = log_file

    def step(self, message: str) -> None:
        """Emit a step header line."""
        self.line(f"==> {message}")

    def summary_lines(self) -> list[str]:
        """Build human-readable summary lines from collected outcomes."""
        lines: list[str] = ["", "Summary"]
        for title, items in (
            ("What already existed:", self.already),
            ("What was skipped:", self.skipped),
            ("What was installed:", self.installed),
            ("What failed (installation continued):", self.failed),
        ):
            if items:
                lines.append("")
                lines.append(title)
                lines.extend(f"  - {m}" for m in items)
        return lines
```

</details>

### ⚙️ Method `add`

```python
def add(self, category: str, message: str) -> None
```

Record a categorized outcome and emit a log line.

<details>
<summary>Code:</summary>

```python
def add(self, category: str, message: str) -> None:
        bucket = {
            "installed": self.installed,
            "already": self.already,
            "skipped": self.skipped,
            "failed": self.failed,
        }.get(category)
        if bucket is not None:
            bucket.append(message)
        prefix = {"installed": "✅", "already": "i", "skipped": "⚠️", "failed": "❌"}.get(category, "•")
        self.line(f"{prefix} {message}")
```

</details>

### ⚙️ Method `detail`

```python
def detail(self, message: str) -> None
```

Emit an indented detail line.

<details>
<summary>Code:</summary>

```python
def detail(self, message: str) -> None:
        self.line(f"    {message}")
```

</details>

### ⚙️ Method `line`

```python
def line(self, message: str) -> None
```

Write a line to the callback and optional log file.

<details>
<summary>Code:</summary>

```python
def line(self, message: str) -> None:
        if self._log is not None:
            self._log(message)
        if self._file is not None:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            with self._file.open("a", encoding="utf-8") as f:
                f.write(message + "\n")
```

</details>

### ⚙️ Method `set_log`

```python
def set_log(self, log: LogFn | None, *, log_file: Path | None = None) -> None
```

Attach a live log callback and optional log file path.

<details>
<summary>Code:</summary>

```python
def set_log(self, log: LogFn | None, *, log_file: Path | None = None) -> None:
        self._log = log
        self._file = log_file
```

</details>

### ⚙️ Method `step`

```python
def step(self, message: str) -> None
```

Emit a step header line.

<details>
<summary>Code:</summary>

```python
def step(self, message: str) -> None:
        self.line(f"==> {message}")
```

</details>

### ⚙️ Method `summary_lines`

```python
def summary_lines(self) -> list[str]
```

Build human-readable summary lines from collected outcomes.

<details>
<summary>Code:</summary>

```python
def summary_lines(self) -> list[str]:
        lines: list[str] = ["", "Summary"]
        for title, items in (
            ("What already existed:", self.already),
            ("What was skipped:", self.skipped),
            ("What was installed:", self.installed),
            ("What failed (installation continued):", self.failed),
        ):
            if items:
                lines.append("")
                lines.append(title)
                lines.extend(f"  - {m}" for m in items)
        return lines
```

</details>
