---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `install_cli.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnInstallCli`](#%EF%B8%8F-class-oninstallcli)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnInstallCli`

```python
class OnInstallCli(ActionBase)
```

Install or reinstall the global `hsk` CLI (`uv tool install -e`).

Puts `hsk` on PATH (typically `%USERPROFILE%\\.local\\bin`). Same step as
`install/harrix-swiss-knife.ps1` after `uv sync`. Rerun after renaming CLI
entry points in `pyproject.toml` or after pulling changes to CLI commands.

<details>
<summary>Code:</summary>

```python
class OnInstallCli(ActionBase):

    icon = "⌨️"
    title = "Install CLI (hsk on PATH)"
    cli_available = True
    cli_hint = "dev install-cli"
    _UV_TOOL_TIMEOUT = 600.0

    @ActionBase.handle_exceptions("install CLI")
    def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        """Run `uv tool install -e` for this repository."""
        if shutil.which("uv") is None:
            self.add_line("❌ uv not found on PATH. Install uv first: https://docs.astral.sh/uv/")
            if not noninteractive:
                self.show_result()
            return

        project_root = h.dev.get_project_root()
        pyproject = project_root / "pyproject.toml"
        if not pyproject.is_file():
            self.add_line(f"❌ pyproject.toml not found: {pyproject}")
            if not noninteractive:
                self.show_result()
            return

        self._project_root = project_root
        self._noninteractive = noninteractive
        if noninteractive:
            self._install_cli_work()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("install CLI thread")
    def in_thread(self) -> None:
        """Install or reinstall the uv tool in a worker thread."""
        self._install_cli_work()

    @ActionBase.handle_exceptions("install CLI completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result after CLI install finishes."""
        if getattr(self, "_install_ok", False):
            self.show_toast("CLI installed (hsk on PATH)")
        else:
            self.show_toast("CLI install finished (see output)")
        self.show_result()

    def _install_cli_work(self) -> None:
        """Install or reinstall the uv tool (shared by GUI thread and CLI)."""
        project_root = self._project_root
        uv = shutil.which("uv") or "uv"
        tool_list = self._run_uv([uv, "tool", "list"])
        reinstall = "harrix-swiss-knife" in tool_list
        cmd = [uv, "tool", "install"]
        if reinstall:
            cmd.append("--reinstall")
        cmd.extend(["-e", str(project_root)])
        self.add_line(f"$ {' '.join(cmd)}")
        result = self._run_uv(cmd)
        if result:
            self.add_line(result)

        hsk_on_path = shutil.which("hsk")
        if hsk_on_path:
            self.add_line(f"✅ `hsk` is on PATH: {hsk_on_path}")
            self._install_ok = True
        else:
            self.add_line(
                "⚠️ `hsk` was not found on PATH after install. "
                "Open a new terminal or ensure %USERPROFILE%\\.local\\bin is on PATH."
            )
            self._install_ok = False

    def _run_uv(self, command: list[str]) -> str:
        """Run a uv argv list and return combined output."""
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=self._UV_TOOL_TIMEOUT,
                shell=False,
            )
        except subprocess.TimeoutExpired:
            return f"Command timed out after {self._UV_TOOL_TIMEOUT} seconds"
        output_parts = [(process.stdout or "").strip(), (process.stderr or "").strip()]
        return "\n".join(filter(None, output_parts))
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None
```

Run `uv tool install -e` for this repository.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, noninteractive: bool = False, **kwargs: Any) -> None:  # noqa: ARG002
        if shutil.which("uv") is None:
            self.add_line("❌ uv not found on PATH. Install uv first: https://docs.astral.sh/uv/")
            if not noninteractive:
                self.show_result()
            return

        project_root = h.dev.get_project_root()
        pyproject = project_root / "pyproject.toml"
        if not pyproject.is_file():
            self.add_line(f"❌ pyproject.toml not found: {pyproject}")
            if not noninteractive:
                self.show_result()
            return

        self._project_root = project_root
        self._noninteractive = noninteractive
        if noninteractive:
            self._install_cli_work()
            return

        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> None
```

Install or reinstall the uv tool in a worker thread.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        self._install_cli_work()
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result after CLI install finishes.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        if getattr(self, "_install_ok", False):
            self.show_toast("CLI installed (hsk on PATH)")
        else:
            self.show_toast("CLI install finished (see output)")
        self.show_result()
```

</details>
