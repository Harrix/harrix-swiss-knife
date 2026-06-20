---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `open_config_json.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnOpenConfigJson`](#%EF%B8%8F-class-onopenconfigjson)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `_editor_token_looks_like_path`](#%EF%B8%8F-method-_editor_token_looks_like_path)
  - [⚙️ Method `_resolve_editor_executable`](#%EF%B8%8F-method-_resolve_editor_executable)
  - [⚙️ Method `_windows_notepad_exe`](#%EF%B8%8F-method-_windows_notepad_exe)

</details>

## 🏛️ Class `OnOpenConfigJson`

```python
class OnOpenConfigJson(ActionBase)
```

Open the application's configuration file.

Opens `config.json` in the editor from `editor`. If that command or path is
missing, tries `cursor`, `code` (VS Code), `code-insiders` in order, writes
the first match back to `config.json` under `editor`, then opens the file.
If none are available on Windows, uses Notepad and persists `editor` as
`notepad`. On other platforms, opens the file with the default application when
no editor is found.

<details>
<summary>Code:</summary>

```python
class OnOpenConfigJson(ActionBase):

    icon = "⚙️"
    title = "Open config.json"

    @ActionBase.handle_exceptions("config file opening")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the application's configuration file."""
        config_file = (h.dev.get_project_root() / self.config_path).resolve()
        editor_raw = str(self.config.get("editor") or "").strip()
        fallback_commands = ("cursor", "code", "code-insiders")

        chosen_key = editor_raw
        resolved: str | None = None

        if editor_raw:
            resolved = self._resolve_editor_executable(editor_raw)

        if resolved is None:
            for name in fallback_commands:
                found = shutil.which(name)
                if found:
                    chosen_key = name
                    resolved = found
                    break

        if resolved is None and sys.platform == "win32":
            found = shutil.which("notepad") or self._windows_notepad_exe()
            if found:
                chosen_key = "notepad"
                resolved = found

        if resolved is not None and chosen_key != editor_raw:
            h.dev.config_update_value("editor", chosen_key, self.config_path)
            self.config["editor"] = chosen_key
            self.add_line(f'Updated "editor" in config.json to: {chosen_key}')

        if resolved is not None:
            commands = f'"{resolved}" "{config_file}"'
            result = h.dev.run_command(commands)
            self.add_line(result)
            return

        if sys.platform == "win32":
            try:
                os.startfile(str(config_file))  # noqa: S606
            except OSError as e:
                self.add_line(f"❌ Could not open config.json: {e}")
            else:
                self.add_line(f"Opened with default app: {config_file}")
                return
        elif sys.platform == "darwin":
            result = h.dev.run_command(f'open "{config_file}"')
            if result:
                self.add_line(result)
            self.add_line(f"Opened with default app: {config_file}")
            return
        else:
            result = h.dev.run_command(f'xdg-open "{config_file}"')
            if result:
                self.add_line(result)
            self.add_line(f"Opened with default app: {config_file}")
            return

        self.add_line("❌ No editor available (configured editor missing; no cursor, code, code-insiders, or notepad).")
        self.add_line(f"Config path: {config_file}")

    def _editor_token_looks_like_path(self, editor: str) -> bool:
        min_windows_drive_len = 2
        return "/" in editor or "\\" in editor or (len(editor) >= min_windows_drive_len and editor[1] == ":")

    def _resolve_editor_executable(self, editor: str) -> str | None:
        """Return a filesystem path to *editor* if it can be launched, else ``None``."""
        editor = editor.strip()
        if not editor:
            return None
        if self._editor_token_looks_like_path(editor):
            try:
                candidate = Path(editor).expanduser().resolve()
            except OSError:
                return None
            return str(candidate) if candidate.is_file() else None
        return shutil.which(editor)

    def _windows_notepad_exe(self) -> str | None:
        system_root = os.environ.get("SYSTEMROOT") or r"C:\Windows"
        notepad = Path(system_root) / "System32" / "notepad.exe"
        return str(notepad) if notepad.is_file() else None
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Open the application's configuration file.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        config_file = (h.dev.get_project_root() / self.config_path).resolve()
        editor_raw = str(self.config.get("editor") or "").strip()
        fallback_commands = ("cursor", "code", "code-insiders")

        chosen_key = editor_raw
        resolved: str | None = None

        if editor_raw:
            resolved = self._resolve_editor_executable(editor_raw)

        if resolved is None:
            for name in fallback_commands:
                found = shutil.which(name)
                if found:
                    chosen_key = name
                    resolved = found
                    break

        if resolved is None and sys.platform == "win32":
            found = shutil.which("notepad") or self._windows_notepad_exe()
            if found:
                chosen_key = "notepad"
                resolved = found

        if resolved is not None and chosen_key != editor_raw:
            h.dev.config_update_value("editor", chosen_key, self.config_path)
            self.config["editor"] = chosen_key
            self.add_line(f'Updated "editor" in config.json to: {chosen_key}')

        if resolved is not None:
            commands = f'"{resolved}" "{config_file}"'
            result = h.dev.run_command(commands)
            self.add_line(result)
            return

        if sys.platform == "win32":
            try:
                os.startfile(str(config_file))  # noqa: S606
            except OSError as e:
                self.add_line(f"❌ Could not open config.json: {e}")
            else:
                self.add_line(f"Opened with default app: {config_file}")
                return
        elif sys.platform == "darwin":
            result = h.dev.run_command(f'open "{config_file}"')
            if result:
                self.add_line(result)
            self.add_line(f"Opened with default app: {config_file}")
            return
        else:
            result = h.dev.run_command(f'xdg-open "{config_file}"')
            if result:
                self.add_line(result)
            self.add_line(f"Opened with default app: {config_file}")
            return

        self.add_line("❌ No editor available (configured editor missing; no cursor, code, code-insiders, or notepad).")
        self.add_line(f"Config path: {config_file}")
```

</details>

### ⚙️ Method `_editor_token_looks_like_path`

```python
def _editor_token_looks_like_path(self, editor: str) -> bool
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _editor_token_looks_like_path(self, editor: str) -> bool:
        min_windows_drive_len = 2
        return "/" in editor or "\\" in editor or (len(editor) >= min_windows_drive_len and editor[1] == ":")
```

</details>

### ⚙️ Method `_resolve_editor_executable`

```python
def _resolve_editor_executable(self, editor: str) -> str | None
```

Return a filesystem path to *editor* if it can be launched, else `None`.

<details>
<summary>Code:</summary>

```python
def _resolve_editor_executable(self, editor: str) -> str | None:
        editor = editor.strip()
        if not editor:
            return None
        if self._editor_token_looks_like_path(editor):
            try:
                candidate = Path(editor).expanduser().resolve()
            except OSError:
                return None
            return str(candidate) if candidate.is_file() else None
        return shutil.which(editor)
```

</details>

### ⚙️ Method `_windows_notepad_exe`

```python
def _windows_notepad_exe(self) -> str | None
```

*No docstring provided.*

<details>
<summary>Code:</summary>

```python
def _windows_notepad_exe(self) -> str | None:
        system_root = os.environ.get("SYSTEMROOT") or r"C:\Windows"
        notepad = Path(system_root) / "System32" / "notepad.exe"
        return str(notepad) if notepad.is_file() else None
```

</details>
