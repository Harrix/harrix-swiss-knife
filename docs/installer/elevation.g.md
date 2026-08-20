---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `elevation.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `is_admin`](#-function-is_admin)
- [🔧 Function `relaunch_elevated`](#-function-relaunch_elevated)

</details>

## 🔧 Function `is_admin`

```python
def is_admin() -> bool
```

Return whether the current process has administrator privileges.

<details>
<summary>Code:</summary>

```python
def is_admin() -> bool:
    if os.name != "nt":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except OSError:
        return False
```

</details>

## 🔧 Function `relaunch_elevated`

```python
def relaunch_elevated(extra_args: list[str]) -> int
```

Relaunch current process with RunAs. Returns Windows ShellExecute result (>32 = OK).

<details>
<summary>Code:</summary>

```python
def relaunch_elevated(extra_args: list[str]) -> int:
    if os.name != "nt":
        msg = "Elevation is Windows-only"
        raise RuntimeError(msg)
    exe = sys.executable
    # When frozen, sys.argv[0] is the exe; otherwise pass -m harrix_swiss_knife.installer
    if getattr(sys, "frozen", False):
        params = " ".join(_quote(a) for a in [*sys.argv[1:], *extra_args])
        target = exe
    else:
        params = " ".join(_quote(a) for a in ["-m", "harrix_swiss_knife.installer", *sys.argv[1:], *extra_args])
        target = exe
    return int(
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            target,
            params,
            None,
            1,
        )
    )
```

</details>
