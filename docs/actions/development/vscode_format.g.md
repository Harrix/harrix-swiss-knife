---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `vscode_format.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnVscodeFormat`](#%EF%B8%8F-class-onvscodeformat)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnVscodeFormat`

```python
class OnVscodeFormat(ActionBase)
```

Run Biome format/fix on the Notes Explorer extension (`npm run format`).

Formats and applies safe fixes under `vscode/harrix-notes-explorer-hsk/`.
Requires Node.js and npm on PATH. Prefer this before `hsk vscode check`.

<details>
<summary>Code:</summary>

```python
class OnVscodeFormat(ActionBase):

    icon = "✨"
    title = "Format VS Code extension"
    cli_available = True
    cli_hint = "vscode format"

    @ActionBase.handle_exceptions("VS Code format")
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Apply Biome write fixes to the VS Code extension."""
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

        self.add_line(f"🔵 Starting Biome format in {extension_dir}")

        try:
            install_proc = ensure_node_modules(extension_dir)
        except FileNotFoundError:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            if not noninteractive:
                self.show_result()
            return

        if install_proc is not None:
            self.add_line("$ npm ci" if (extension_dir / "package-lock.json").is_file() else "$ npm install")
            output = "\n".join(part for part in (install_proc.stdout.strip(), install_proc.stderr.strip()) if part)
            if output:
                self.add_line(output)
            if install_proc.returncode != 0:
                self.add_line(f"❌ npm install failed (exit code {install_proc.returncode}).")
                if not noninteractive:
                    self.show_result()
                return

        self.add_line("$ npm run format")
        process = run_npm(extension_dir, "run", "format")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ npm run format failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ Biome format completed.")

        if not noninteractive:
            self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Apply Biome write fixes to the VS Code extension.

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

        self.add_line(f"🔵 Starting Biome format in {extension_dir}")

        try:
            install_proc = ensure_node_modules(extension_dir)
        except FileNotFoundError:
            self.add_line("❌ npm not found on PATH. Install Node.js, then retry.")
            if not noninteractive:
                self.show_result()
            return

        if install_proc is not None:
            self.add_line("$ npm ci" if (extension_dir / "package-lock.json").is_file() else "$ npm install")
            output = "\n".join(part for part in (install_proc.stdout.strip(), install_proc.stderr.strip()) if part)
            if output:
                self.add_line(output)
            if install_proc.returncode != 0:
                self.add_line(f"❌ npm install failed (exit code {install_proc.returncode}).")
                if not noninteractive:
                    self.show_result()
                return

        self.add_line("$ npm run format")
        process = run_npm(extension_dir, "run", "format")
        output = "\n".join(part for part in (process.stdout.strip(), process.stderr.strip()) if part)
        if output:
            self.add_line(output)

        if process.returncode != 0:
            self.add_line(f"❌ npm run format failed (exit code {process.returncode}).")
        else:
            self.add_line("✅ Biome format completed.")

        if not noninteractive:
            self.show_result()
```

</details>
