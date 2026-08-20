---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `progress_ui.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `ProgressBarMode`](#%EF%B8%8F-class-progressbarmode)
- [🔧 Function `progress_mode_for_log_line`](#-function-progress_mode_for_log_line)

</details>

## 🏛️ Class `ProgressBarMode`

```python
class ProgressBarMode(Enum)
```

How the install progress bar should look.

<details>
<summary>Code:</summary>

```python
class ProgressBarMode(Enum):

    INDETERMINATE = auto()
    DETERMINATE = auto()
    COMPLETE = auto()
```

</details>

## 🔧 Function `progress_mode_for_log_line`

```python
def progress_mode_for_log_line(line: str, *, extracting: bool) -> ProgressBarMode | None
```

Return a progress mode change for a log line, or `None` to leave the bar alone.

Payload extract keeps a determinate byte/file progress. Any later `==>` step
switches to an indeterminate busy bar so a finished extract does not leave 100%.

<details>
<summary>Code:</summary>

```python
def progress_mode_for_log_line(line: str, *, extracting: bool) -> ProgressBarMode | None:
    text = line.strip()
    if not text:
        return None
    if text.startswith("==> "):
        if "extract" in text.lower():
            return ProgressBarMode.DETERMINATE
        return ProgressBarMode.INDETERMINATE
    if extracting:
        return None
    return None
```

</details>
