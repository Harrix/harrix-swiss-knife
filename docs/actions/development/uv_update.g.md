---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uv_update.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnUvUpdate`](#️-class-onuvupdate)
  - [⚙️ Method `execute`](#️-method-execute)
  - [⚙️ Method `in_thread`](#️-method-in_thread)
  - [⚙️ Method `thread_after`](#️-method-thread_after)

</details>

## 🏛️ Class `OnUvUpdate`

```python
class OnUvUpdate(ActionBase)
```

Update uv package manager to its latest version.

Tries `uv self update` (standalone uv only), then on Windows `winget upgrade` /
`winget install` for `astral-sh.uv`, then `python -m pip install --upgrade uv`
(prefers `python.exe` over `pythonw.exe` when the GUI launcher has no pip).

<details>
<summary>Code:</summary>

```python
class OnUvUpdate(ActionBase):

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
        result = h.dev.run_command("uv self update")
        blocks: list[str] = [f"=== uv self update ===\n{result}"]

        if not isinstance(result, str) or self._UV_SELF_UPDATE_BLOCKED not in result:
            return result

        if sys.platform == "win32" and shutil.which("winget"):
            upgrade = (
                "winget upgrade -e --id astral-sh.uv --source winget "
                "--accept-package-agreements --accept-source-agreements --silent"
            )
            winget_out = h.dev.run_command(upgrade)
            blocks.append(f"\n=== winget upgrade (astral-sh.uv) ===\n{winget_out}")
            if "no installed package" in winget_out.lower():
                install = (
                    "winget install -e --id astral-sh.uv --source winget "
                    "--accept-package-agreements --accept-source-agreements --silent"
                )
                blocks.append(f"\n=== winget install (astral-sh.uv) ===\n{h.dev.run_command(install)}")

        pip_sections = [
            f"--- {py_exe} ---\n{self._pip_install_upgrade_uv_log(py_exe)}"
            for py_exe in self._python_candidates_for_pip()
        ]
        blocks.append("\n=== pip (venv / current interpreters) ===\n" + "\n\n".join(pip_sections))

        blocks.append(
            "\n=== If uv is still not updated ===\n"
            "Install the standalone binary: https://docs.astral.sh/uv/getting-started/installation/\n"
            "Or run: powershell -NoProfile -ExecutionPolicy Bypass -Command "
            "'irm https://astral.sh/uv/install.ps1 | iex'"
        )
        return "\n".join(blocks)

    @ActionBase.handle_exceptions("uv update thread completion")
    def thread_after(self, result: Any) -> None:
        """Execute code in the main thread after in_thread(). For handling the results of thread execution."""
        self.show_toast("UV update steps finished (see output)")
        self.add_line(result)
        self.show_result()

    def _pip_install_upgrade_uv_log(self, py_exe: Path) -> str:
        """Run pip upgrade for uv; bootstrap pip with ensurepip when missing."""
        quoted = f'"{py_exe}"'
        pip_cmd = f"{quoted} -m pip install --upgrade uv"
        lines = [pip_cmd]
        pip_out = h.dev.run_command(pip_cmd)
        lines.append(pip_out)
        if "No module named pip" in pip_out:
            ensure_cmd = f"{quoted} -m ensurepip --upgrade"
            lines.append(ensure_cmd)
            lines.append(h.dev.run_command(ensure_cmd))
            lines.append(pip_cmd)
            lines.append(h.dev.run_command(pip_cmd))
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
        result = h.dev.run_command("uv self update")
        blocks: list[str] = [f"=== uv self update ===\n{result}"]

        if not isinstance(result, str) or self._UV_SELF_UPDATE_BLOCKED not in result:
            return result

        if sys.platform == "win32" and shutil.which("winget"):
            upgrade = (
                "winget upgrade -e --id astral-sh.uv --source winget "
                "--accept-package-agreements --accept-source-agreements --silent"
            )
            winget_out = h.dev.run_command(upgrade)
            blocks.append(f"\n=== winget upgrade (astral-sh.uv) ===\n{winget_out}")
            if "no installed package" in winget_out.lower():
                install = (
                    "winget install -e --id astral-sh.uv --source winget "
                    "--accept-package-agreements --accept-source-agreements --silent"
                )
                blocks.append(f"\n=== winget install (astral-sh.uv) ===\n{h.dev.run_command(install)}")

        pip_sections = [
            f"--- {py_exe} ---\n{self._pip_install_upgrade_uv_log(py_exe)}"
            for py_exe in self._python_candidates_for_pip()
        ]
        blocks.append("\n=== pip (venv / current interpreters) ===\n" + "\n\n".join(pip_sections))

        blocks.append(
            "\n=== If uv is still not updated ===\n"
            "Install the standalone binary: https://docs.astral.sh/uv/getting-started/installation/\n"
            "Or run: powershell -NoProfile -ExecutionPolicy Bypass -Command "
            "'irm https://astral.sh/uv/install.ps1 | iex'"
        )
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
