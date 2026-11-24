---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `adb.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `adb_pull`](#-function-adb_pull)
- [🔧 Function `adb_push`](#-function-adb_push)
- [🔧 Function `adb_shell_getprop`](#-function-adb_shell_getprop)
- [🔧 Function `list_adb_device_states`](#-function-list_adb_device_states)
- [🔧 Function `resolve_adb`](#-function-resolve_adb)

</details>

## 🔧 Function `adb_pull`

```python
def adb_pull(adb: Path, serial: str, remote_path: str, local_path: Path) -> subprocess.CompletedProcess[str]
```

Pull a remote file onto the PC with ``adb -s SERIAL pull``.

<details>
<summary>Code:</summary>

```python
def adb_pull(adb: Path, serial: str, remote_path: str, local_path: Path) -> subprocess.CompletedProcess[str]:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    return _run_adb(
        adb,
        ["-s", serial, "pull", remote_path, str(local_path)],
    )
```

</details>

## 🔧 Function `adb_push`

```python
def adb_push(adb: Path, serial: str, local_path: Path, remote_path: str) -> subprocess.CompletedProcess[str]
```

Push a local file to the device with ``adb -s SERIAL push``.

<details>
<summary>Code:</summary>

```python
def adb_push(adb: Path, serial: str, local_path: Path, remote_path: str) -> subprocess.CompletedProcess[str]:
    return _run_adb(
        adb,
        ["-s", serial, "push", str(local_path), remote_path],
    )
```

</details>

## 🔧 Function `adb_shell_getprop`

```python
def adb_shell_getprop(adb: Path, serial: str, prop: str) -> str | None
```

Return a trimmed ``getprop`` value from a device, or ``None``.

<details>
<summary>Code:</summary>

```python
def adb_shell_getprop(adb: Path, serial: str, prop: str) -> str | None:
    process = _run_adb(adb, ["-s", serial, "shell", "getprop", prop])
    if process.returncode != 0:
        return None
    value = (process.stdout or "").strip()
    return value or None
```

</details>

## 🔧 Function `list_adb_device_states`

```python
def list_adb_device_states(adb: Path) -> tuple[list[str], list[str], str]
```

Return `(authorized, unauthorized, combined_output)` from `adb devices`.

`combined_output` is non-empty when the command fails or prints diagnostics.

<details>
<summary>Code:</summary>

```python
def list_adb_device_states(adb: Path) -> tuple[list[str], list[str], str]:
    process = _run_adb(adb, ["devices"])
    combined = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
    if process.returncode != 0:
        return [], [], combined

    authorized: list[str] = []
    unauthorized: list[str] = []
    for raw_line in (process.stdout or "").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("List of devices"):
            continue
        parts = stripped.split()
        if len(parts) < _MIN_DEVICE_COLUMNS:
            continue
        serial, state = parts[0], parts[1]
        if state == "device":
            authorized.append(serial)
        elif state == "unauthorized":
            unauthorized.append(serial)
    return authorized, unauthorized, ""
```

</details>

## 🔧 Function `resolve_adb`

```python
def resolve_adb() -> Path | None
```

Resolve ``adb`` / ``adb.exe`` from Android SDK or ``PATH``.

<details>
<summary>Code:</summary>

```python
def resolve_adb() -> Path | None:
    android_home = resolve_android_home()
    if android_home:
        exe_name = "adb.exe" if sys.platform == "win32" else "adb"
        candidate = Path(android_home) / "platform-tools" / exe_name
        if candidate.is_file():
            return candidate

    which_cmd = "where adb" if sys.platform == "win32" else "which adb"
    which = h.dev.run_command(which_cmd, is_shell=True)
    for line in (which or "").splitlines():
        path = Path(line.strip().strip('"'))
        if path.is_file():
            return path
    return None
```

</details>
