---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uv_upgrade_bat.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_relaunch_command`](#-function-build_relaunch_command)
- [🔧 Function `build_uv_upgrade_cmd`](#-function-build_uv_upgrade_cmd)
- [🔧 Function `quote_cmd_arg`](#-function-quote_cmd_arg)
- [🔧 Function `read_python_version_pin`](#-function-read_python_version_pin)
- [🔧 Function `resolve_upgrade_projects`](#-function-resolve_upgrade_projects)
- [🔧 Function `write_uv_upgrade_cmd`](#-function-write_uv_upgrade_cmd)

</details>

## 🔧 Function `build_relaunch_command`

```python
def build_relaunch_command(argv: Sequence[str]) -> str
```

Return a space-joined cmd line for restarting with the same argv.

<details>
<summary>Code:</summary>

```python
def build_relaunch_command(argv: Sequence[str]) -> str:
    return " ".join(quote_cmd_arg(part) for part in argv)
```

</details>

## 🔧 Function `build_uv_upgrade_cmd`

```python
def build_uv_upgrade_cmd(*, wait_pid: int, uv_exe: Path, project_dirs: Sequence[Path], relaunch_argv: Sequence[str], log_path: Path | None = None, wait_timeout_seconds: int = WAIT_TIMEOUT_SECONDS, close_cursor: bool = True) -> str
```

Return the text of a `.cmd` that waits for HSK, upgrades, then relaunches.

Optionally closes Cursor first so uv-managed Python installs are not locked.
`uv python upgrade` is scoped to each project's `.python-version` when present
and is non-fatal so `uv sync --upgrade` can still run. On hard failure the
script still relaunches after [`pause`](apps/fitness/lightbox_logic.g.md#%EF%B8%8F-method-pause).

<details>
<summary>Code:</summary>

```python
def build_uv_upgrade_cmd(
    *,
    wait_pid: int,
    uv_exe: Path,
    project_dirs: Sequence[Path],
    relaunch_argv: Sequence[str],
    log_path: Path | None = None,
    wait_timeout_seconds: int = WAIT_TIMEOUT_SECONDS,
    close_cursor: bool = True,
) -> str:
    uv = str(uv_exe)
    log = str(log_path) if log_path is not None else str(Path(os.environ.get("TEMP", ".")) / _LOG_NAME)
    relaunch = build_relaunch_command(relaunch_argv)
    lines: list[str] = [
        "@echo off",
        "setlocal EnableExtensions",
        f'set "UV={uv}"',
        f'set "LOG={log}"',
        f"set WAIT_PID={wait_pid}",
        f"set WAIT_MAX={wait_timeout_seconds}",
        f'set "CURSOR_EXE={CURSOR_PROCESS_NAME}"',
        'echo HSK uv package upgrade > "%LOG%"',
        "echo Waiting for process %WAIT_PID% to exit...",
        'echo Waiting for process %WAIT_PID% to exit...>> "%LOG%"',
        "set /a waited=0",
        ":wait_loop",
        'tasklist /FI "PID eq %WAIT_PID%" 2>nul | find "%WAIT_PID%" >nul',
        "if errorlevel 1 goto wait_done",
        "if %waited% geq %WAIT_MAX% (",
        '  echo Timed out waiting for PID %WAIT_PID%.>> "%LOG%"',
        "  echo Timed out waiting for PID %WAIT_PID%. Continuing anyway.",
        "  goto wait_done",
        ")",
        "timeout /t 1 /nobreak >nul",
        "set /a waited+=1",
        "goto wait_loop",
        ":wait_done",
    ]
    if close_cursor:
        lines.extend(
            [
                "echo.",
                "echo === Closing Cursor if running ===",
                'echo === Closing Cursor if running ===>> "%LOG%"',
                'tasklist /FI "IMAGENAME eq %CURSOR_EXE%" 2>nul | find /I "%CURSOR_EXE%" >nul',
                "if errorlevel 1 (",
                "  echo Cursor is not running.",
                '  echo Cursor is not running.>> "%LOG%"',
                "  goto cursor_done",
                ")",
                "echo Closing %CURSOR_EXE% so Python installs are not locked...",
                'echo Closing %CURSOR_EXE% so Python installs are not locked...>> "%LOG%"',
                'taskkill /IM "%CURSOR_EXE%" /T /F >> "%LOG%" 2>&1',
                "set /a waited=0",
                ":cursor_wait",
                'tasklist /FI "IMAGENAME eq %CURSOR_EXE%" 2>nul | find /I "%CURSOR_EXE%" >nul',
                "if errorlevel 1 goto cursor_gone",
                "if %waited% geq %WAIT_MAX% (",
                '  echo Timed out waiting for Cursor to exit.>> "%LOG%"',
                "  echo Timed out waiting for Cursor to exit. Continuing anyway.",
                "  goto cursor_done",
                ")",
                "timeout /t 1 /nobreak >nul",
                "set /a waited+=1",
                "goto cursor_wait",
                ":cursor_gone",
                "echo Cursor closed.",
                'echo Cursor closed.>> "%LOG%"',
                f"timeout /t {_POST_CLOSE_SETTLE_SECONDS} /nobreak >nul",
                ":cursor_done",
            ]
        )
    lines.extend(
        [
            "echo.",
            "echo === uv self update ===",
            'echo === uv self update ===>> "%LOG%"',
            '"%UV%" self update',
            "if errorlevel 1 (",
            '  echo uv self update failed.>> "%LOG%"',
            "  goto fail",
            ")",
        ]
    )
    for project in project_dirs:
        root = str(project)
        pin = read_python_version_pin(project)
        upgrade_args = f" {pin}" if pin else ""
        pin_note = f" ({pin})" if pin else " (all installed)"
        lines.extend(
            [
                "echo.",
                f"echo === {project.name}: uv python upgrade{pin_note} ===",
                f'echo === {project.name}: uv python upgrade{pin_note} ===>> "%LOG%"',
                f"cd /d {quote_cmd_arg(root)}",
                "if errorlevel 1 (",
                f'  echo cd failed for {project.name}.>> "%LOG%"',
                "  goto fail",
                ")",
                f'"%UV%" python upgrade{upgrade_args}',
                "if errorlevel 1 (",
                f'  echo WARNING: uv python upgrade failed in {project.name}; continuing with sync.>> "%LOG%"',
                f"  echo WARNING: uv python upgrade failed in {project.name}; continuing with sync.",
                ")",
                f"echo === {project.name}: uv sync --upgrade ===",
                f'echo === {project.name}: uv sync --upgrade ===>> "%LOG%"',
                '"%UV%" sync --upgrade',
                "if errorlevel 1 (",
                f'  echo uv sync --upgrade failed in {project.name}.>> "%LOG%"',
                "  goto fail",
                ")",
            ]
        )
    lines.extend(
        [
            "echo.",
            "echo === Upgrade finished ===",
            'echo === Upgrade finished ===>> "%LOG%"',
            "goto relaunch",
            ":fail",
            "echo.",
            "echo Upgrade failed. See log: %LOG%",
            'echo Upgrade failed. See log: %LOG%>> "%LOG%"',
            "pause",
            ":relaunch",
            "echo Relaunching Harrix Swiss Knife...",
            'echo Relaunching Harrix Swiss Knife...>> "%LOG%"',
            f'start "" {relaunch}',
            "endlocal",
            "exit /b 0",
            "",
        ]
    )
    return "\r\n".join(lines)
```

</details>

## 🔧 Function `quote_cmd_arg`

```python
def quote_cmd_arg(value: str) -> str
```

Quote a single argument for `cmd.exe` / `CreateProcess` style parsing.

<details>
<summary>Code:</summary>

```python
def quote_cmd_arg(value: str) -> str:
    if not value:
        return '""'
    if re.search(r'[\s"&<>|^]', value) is None:
        return value
    escaped = value.replace('"', '""')
    return f'"{escaped}"'
```

</details>

## 🔧 Function `read_python_version_pin`

```python
def read_python_version_pin(project_dir: Path) -> str | None
```

Return the first non-empty line from `.python-version`, if any.

<details>
<summary>Code:</summary>

```python
def read_python_version_pin(project_dir: Path) -> str | None:
    path = project_dir / ".python-version"
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        pin = line.strip()
        if pin and not pin.startswith("#"):
            return pin
    return None
```

</details>

## 🔧 Function `resolve_upgrade_projects`

```python
def resolve_upgrade_projects(paths_python_projects: Sequence[object]) -> list[Path]
```

Return existing dirs for the three Harrix projects from config paths.

Args:

- `paths_python_projects` (`Sequence[object]`): Entries from `config.json`.

Returns:

- `list[Path]`: Resolved project roots in `PROJECT_NAMES` order (missing skipped).

<details>
<summary>Code:</summary>

```python
def resolve_upgrade_projects(paths_python_projects: Sequence[object]) -> list[Path]:
    by_name: dict[str, Path] = {}
    for entry in paths_python_projects:
        path = Path(str(entry)).expanduser()
        name = path.name
        if name not in PROJECT_NAMES or name in by_name:
            continue
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved.is_dir():
            by_name[name] = resolved
    return [by_name[name] for name in PROJECT_NAMES if name in by_name]
```

</details>

## 🔧 Function `write_uv_upgrade_cmd`

```python
def write_uv_upgrade_cmd(path: Path, *, wait_pid: int, uv_exe: Path, project_dirs: Sequence[Path], relaunch_argv: Sequence[str], log_path: Path | None = None, wait_timeout_seconds: int = WAIT_TIMEOUT_SECONDS, close_cursor: bool = True) -> Path
```

Write the upgrade `.cmd` to `path` and return `path`.

<details>
<summary>Code:</summary>

```python
def write_uv_upgrade_cmd(
    path: Path,
    *,
    wait_pid: int,
    uv_exe: Path,
    project_dirs: Sequence[Path],
    relaunch_argv: Sequence[str],
    log_path: Path | None = None,
    wait_timeout_seconds: int = WAIT_TIMEOUT_SECONDS,
    close_cursor: bool = True,
) -> Path:
    text = build_uv_upgrade_cmd(
        wait_pid=wait_pid,
        uv_exe=uv_exe,
        project_dirs=project_dirs,
        relaunch_argv=relaunch_argv,
        log_path=log_path,
        wait_timeout_seconds=wait_timeout_seconds,
        close_cursor=close_cursor,
    )
    path.write_text(text, encoding="utf-8", newline="")
    return path
```

</details>
