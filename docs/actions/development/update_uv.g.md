---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `update_uv.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnUpdateUv`](#%EF%B8%8F-class-onupdateuv)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnUpdateUv`

```python
class OnUpdateUv(ActionBase)
```

Update uv package manager to its latest version.

Tries `uv self update` (standalone uv only), then on Windows `winget upgrade` /
`winget install` for `astral-sh.uv`, then `python -m pip install --upgrade uv`
(prefers `python.exe` over `pythonw.exe` when the GUI launcher has no pip).

Resolves `uv` via PATH and common install locations (including
`%USERPROFILE%\.local\bin` from the GUI installer), because tray shortcuts
often inherit a stale Explorer PATH.

<details>
<summary>Code:</summary>

```python
class OnUpdateUv(ActionBase):

    icon = "📥"
    title = "Update uv"

    _UV_SELF_UPDATE_BLOCKED = (
        "Self-update is only available for uv binaries installed via the standalone installation scripts"
    )

    @ActionBase.handle_exceptions("uv update")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Update uv package manager to its latest version."""
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("uv update thread")
    def in_thread(self) -> str | None:
        """Execute code in a separate thread. For performing long-running operations."""
        refresh_path()
        uv = find_uv_exe()
        if uv is None:
            blocks = [
                (
                    "=== uv self update ===\n"
                    "❌ uv not found on PATH or in common install locations "
                    "(checked %USERPROFILE%\\.local\\bin and WinGet links)."
                )
            ]
            blocks.extend(self._windows_winget_blocks())
            blocks.append(self._manual_install_hint())
            return "\n".join(blocks)

        result = h.dev.run_command([str(uv), "self", "update"], is_shell=False)
        blocks: list[str] = [f"=== uv self update ({uv}) ===\n{result}"]

        if not isinstance(result, str) or self._UV_SELF_UPDATE_BLOCKED not in result:
            return "\n".join(blocks)

        blocks.extend(self._windows_winget_blocks())

        pip_sections = [
            f"--- {py_exe} ---\n{self._pip_install_upgrade_uv_log(py_exe)}"
            for py_exe in self._python_candidates_for_pip()
        ]
        blocks.append("\n=== pip (venv / current interpreters) ===\n" + "\n\n".join(pip_sections))
        blocks.append(self._manual_install_hint())
        return "\n".join(blocks)

    @ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("UV update steps finished (see output)")
        self.add_line(result)
        self.show_result()

    @staticmethod
    def _manual_install_hint() -> str:
        return (
            "\n=== If uv is still not updated ===\n"
            "Install the standalone binary: https://docs.astral.sh/uv/getting-started/installation/\n"
            "Or run: powershell -NoProfile -ExecutionPolicy Bypass -Command "
            "'irm https://astral.sh/uv/install.ps1 | iex'"
        )

    def _pip_install_upgrade_uv_log(self, py_exe: Path) -> str:
        """Run pip upgrade for uv; bootstrap pip with ensurepip when missing."""
        quoted = f'"{py_exe}"'
        pip_cmd = f"{quoted} -m pip install --upgrade uv"
        lines = [pip_cmd]
        pip_out = h.dev.run_command(pip_cmd, is_shell=True)
        lines.append(pip_out)
        if "No module named pip" in pip_out:
            ensure_cmd = f"{quoted} -m ensurepip --upgrade"
            lines.append(ensure_cmd)
            lines.append(h.dev.run_command(ensure_cmd, is_shell=True))
            lines.append(pip_cmd)
            lines.append(h.dev.run_command(pip_cmd, is_shell=True))
        return "\n".join(lines)

    @staticmethod
    def _python_candidates_for_pip() -> list[Path]:
        """Return interpreter paths to try for `python -m pip` (GUI apps often run as `pythonw.exe`)."""
        exe = Path(sys.executable).resolve()
        candidates: list[Path] = []
        if exe.name.lower() == "pythonw.exe":
            console = exe.with_name("python.exe")
            if console.is_file():
                candidates.append(console)
        candidates.append(exe)
        seen: set[Path] = set()
        unique: list[Path] = []
        for p in candidates:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def _windows_winget_blocks(self) -> list[str]:
        """Run winget upgrade/install for astral-sh.uv when available."""
        if sys.platform != "win32":
            return []
        winget = shutil.which("winget")
        if not winget:
            winget_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "winget.exe"
            winget = str(winget_path) if winget_path.is_file() else None
        if not winget:
            return ["\n=== winget ===\nwinget not found; skipped."]

        quoted = f'"{winget}"'
        upgrade = (
            f"{quoted} upgrade -e --id astral-sh.uv --source winget "
            "--accept-package-agreements --accept-source-agreements --silent"
        )
        winget_out = h.dev.run_command(upgrade, is_shell=True)
        blocks = [f"\n=== winget upgrade (astral-sh.uv) ===\n{winget_out}"]
        if "no installed package" in winget_out.lower():
            install = (
                f"{quoted} install -e --id astral-sh.uv --source winget "
                "--accept-package-agreements --accept-source-agreements --silent"
            )
            blocks.append(f"\n=== winget install (astral-sh.uv) ===\n{h.dev.run_command(install, is_shell=True)}")
        return blocks
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Update uv package manager to its latest version.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
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
        refresh_path()
        uv = find_uv_exe()
        if uv is None:
            blocks = [
                (
                    "=== uv self update ===\n"
                    "❌ uv not found on PATH or in common install locations "
                    "(checked %USERPROFILE%\\.local\\bin and WinGet links)."
                )
            ]
            blocks.extend(self._windows_winget_blocks())
            blocks.append(self._manual_install_hint())
            return "\n".join(blocks)

        result = h.dev.run_command([str(uv), "self", "update"], is_shell=False)
        blocks: list[str] = [f"=== uv self update ({uv}) ===\n{result}"]

        if not isinstance(result, str) or self._UV_SELF_UPDATE_BLOCKED not in result:
            return "\n".join(blocks)

        blocks.extend(self._windows_winget_blocks())

        pip_sections = [
            f"--- {py_exe} ---\n{self._pip_install_upgrade_uv_log(py_exe)}"
            for py_exe in self._python_candidates_for_pip()
        ]
        blocks.append("\n=== pip (venv / current interpreters) ===\n" + "\n\n".join(pip_sections))
        blocks.append(self._manual_install_hint())
        return "\n".join(blocks)
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
        self.show_toast("UV update steps finished (see output)")
        self.add_line(result)
        self.show_result()
```

</details>
