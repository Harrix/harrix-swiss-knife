---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `vscode_check.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnVscodeCheck`](#%EF%B8%8F-class-onvscodecheck)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnVscodeCheck`

```python
class OnVscodeCheck(ActionBase)
```

Run Biome check on the Notes Explorer extension (`npm run check`).

Lints and verifies formatting under `vscode/harrix-notes-explorer-hsk/`.
Requires Node.js and npm on PATH. Prefer `hsk vscode format` first.

<details>
<summary>Code:</summary>

```python
class OnVscodeCheck(ActionBase):

    icon = "🔬"
    title = "Check VS Code extension"
    cli_available = True
    cli_hint = "vscode check"

    @ActionBase.handle_exceptions("vs code check")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Run Biome check (sync for CLI, background thread for tray)."""
        extension_dir = resolve_extension_dir()
        if extension_dir is None:
            self.add_line("❌ vscode/harrix-notes-explorer-hsk or package.json not found.")
            if not noninteractive:
                self.show_result()
            return

        if resolve_npm() is None:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            self._run_biome_check(extension_dir)
            return

        self.folder_path = extension_dir
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("vs code check thread")
    def in_thread(self) -> str | None:
        """Run Biome check in a worker thread for the tray UI."""
        extension_dir = getattr(self, "folder_path", None)
        if extension_dir is None:
            return None
        self._run_biome_check(extension_dir)
        return None

    @ActionBase.handle_exceptions("vs code check thread completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after a tray check."""
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()

    def _run_biome_check(self, extension_dir: Path) -> None:
        """Ensure deps and run ``npm run check``."""
        self.add_line(f"🔵 Starting Biome check in {extension_dir}")

        try:
            install_proc = ensure_node_modules(extension_dir)
        except FileNotFoundError:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            return

        if install_proc is not None:
            self.add_line("$ npm ci" if (extension_dir / "package-lock.json").is_file() else "$ npm install")
            output = "\n".join(part for part in (install_proc.stdout.strip(), install_proc.stderr.strip()) if part)
            if output:
                self.add_line(output)
            if install_proc.returncode != 0:
                self.add_line(f"❌ npm install failed (exit code {install_proc.returncode}).")
                return

        self.add_line("$ npm run check")
        process = run_npm(extension_dir, "run", "check")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ npm run check failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ Biome check completed.")
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Run Biome check (sync for CLI, background thread for tray).

<details>
<summary>Code:</summary>

```python
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        extension_dir = resolve_extension_dir()
        if extension_dir is None:
            self.add_line("❌ vscode/harrix-notes-explorer-hsk or package.json not found.")
            if not noninteractive:
                self.show_result()
            return

        if resolve_npm() is None:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            self._run_biome_check(extension_dir)
            return

        self.folder_path = extension_dir
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> str | None
```

Run Biome check in a worker thread for the tray UI.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> str | None:
        extension_dir = getattr(self, "folder_path", None)
        if extension_dir is None:
            return None
        self._run_biome_check(extension_dir)
        return None
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after a tray check.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        failed = any(isinstance(line, str) and line.strip().startswith("❌") for line in self.result_lines)
        self.show_toast(f"{self.title} {'failed' if failed else 'completed'}")
        self.show_result()
```

</details>
