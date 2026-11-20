---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_restart.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `gui_relaunch_argv`](#-function-gui_relaunch_argv)
- [🔧 Function `restart_argv`](#-function-restart_argv)
- [🔧 Function `restart_current_application`](#-function-restart_current_application)
- [🔧 Function `spawn_replacement_process`](#-function-spawn_replacement_process)

</details>

## 🔧 Function `gui_relaunch_argv`

```python
def gui_relaunch_argv() -> list[str]
```

Return argv that relaunches this app without a console window on Windows.

Prefers sibling `pythonw.exe` when the current interpreter is `python.exe`
(for example a Cursor terminal launch), so the restarted tray app does not
open a black console. Falls back to `restart_argv()` when `pythonw.exe` is
missing or the process is already a GUI wrapper.

Returns:

- `list[str]`: Interpreter path followed by `sys.argv`.

<details>
<summary>Code:</summary>

```python
def gui_relaunch_argv() -> list[str]:
    current = Path(sys.executable)
    name = current.name.casefold()
    if name == "python.exe":
        pythonw = current.with_name("pythonw.exe")
        if pythonw.is_file():
            return [str(pythonw), *sys.argv]
    return restart_argv()
```

</details>

## 🔧 Function `restart_argv`

```python
def restart_argv() -> list[str]
```

Return argv that starts the same interpreter and entry script.

Returns:

- `list[str]`: `sys.executable` followed by `sys.argv`.

<details>
<summary>Code:</summary>

```python
def restart_argv() -> list[str]:
    return [sys.executable, *sys.argv]
```

</details>

## 🔧 Function `restart_current_application`

```python
def restart_current_application() -> bool
```

Spawn a replacement process, then quit the current Qt application.

Releases the single-instance socket first so the new process can become
primary instead of asking this one to show the command window.

Returns:

- `bool`: `True` when the new process was started.

<details>
<summary>Code:</summary>

```python
def restart_current_application() -> bool:
    held = release_held_instance()
    if not spawn_replacement_process():
        if held is not None:
            restore_held_instance(held)
        return False
    app = QApplication.instance()
    if app is not None:
        app.quit()
    return True
```

</details>

## 🔧 Function `spawn_replacement_process`

```python
def spawn_replacement_process(argv: list[str] | None = None) -> subprocess.Popen[str] | None
```

Start a detached copy of this process.

Args:

- `argv` (`list[str] | None`): Command to start. Defaults to `restart_argv()`.

Returns:

- `subprocess.Popen[str] | None`: The new process, or `None` on failure.

<details>
<summary>Code:</summary>

```python
def spawn_replacement_process(argv: list[str] | None = None) -> subprocess.Popen[str] | None:
    command = list(argv) if argv is not None else restart_argv()
    if not command:
        return None
    kwargs: dict[str, Any] = {"close_fds": True}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    try:
        return subprocess.Popen(command, **kwargs)
    except OSError:
        return None
```

</details>
