---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `install_harrix_notes_explorer_extension.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnInstallHarrixNotesExplorerExtension`](#%EF%B8%8F-class-oninstallharrixnotesexplorerextension)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `_all_supported_win32_editor_labels`](#%EF%B8%8F-method-_all_supported_win32_editor_labels)
  - [⚙️ Method `_antigravity_installed_win32`](#%EF%B8%8F-method-_antigravity_installed_win32)
  - [⚙️ Method `_canonical_editor_label`](#%EF%B8%8F-method-_canonical_editor_label)
  - [⚙️ Method `_cursor_installed_win32`](#%EF%B8%8F-method-_cursor_installed_win32)
  - [⚙️ Method `_dest_extension_roots`](#%EF%B8%8F-method-_dest_extension_roots)
  - [⚙️ Method `_discover_win32_editors`](#%EF%B8%8F-method-_discover_win32_editors)
  - [⚙️ Method `_editor_choice_label`](#%EF%B8%8F-method-_editor_choice_label)
  - [⚙️ Method `_install_for_editors`](#%EF%B8%8F-method-_install_for_editors)
  - [⚙️ Method `_is_harrix_notes_explorer_installed`](#%EF%B8%8F-method-_is_harrix_notes_explorer_installed)
  - [⚙️ Method `_merge_harrix_notes_explorer_extensions_json`](#%EF%B8%8F-method-_merge_harrix_notes_explorer_extensions_json)
  - [⚙️ Method `_resolve_editor_cli_token`](#%EF%B8%8F-method-_resolve_editor_cli_token)
  - [⚙️ Method `_vscode_extensions_json_uri_path`](#%EF%B8%8F-method-_vscode_extensions_json_uri_path)
  - [⚙️ Method `_vscode_insiders_installed_win32`](#%EF%B8%8F-method-_vscode_insiders_installed_win32)
  - [⚙️ Method `_vscode_stable_installed_win32`](#%EF%B8%8F-method-_vscode_stable_installed_win32)
  - [⚙️ Method `_vscodium_installed_win32`](#%EF%B8%8F-method-_vscodium_installed_win32)
  - [⚙️ Method `_windsurf_installed_win32`](#%EF%B8%8F-method-_windsurf_installed_win32)

</details>

## 🏛️ Class `OnInstallHarrixNotesExplorerExtension`

```python
class OnInstallHarrixNotesExplorerExtension(ActionBase)
```

Install or update the bundled Harrix Notes Explorer (HSK) VS Code extension into local profiles.

Shows a checkbox dialog listing all supported VS Code-family editors (stable order). Detected
installs are selectable; missing installs appear as `(not installed)` and are disabled. Editors
that already have `harrix-notes-explorer-hsk` are checked by default. Copies the
`vscode/harrix-notes-explorer-hsk` tree into `harrix-notes-explorer-hsk` under each selected editor's
`extensions` folder (no symlinks or elevation required for typical user profiles), then upserts
an entry in that directory's `extensions.json` so current VS Code builds list the extension.

<details>
<summary>Code:</summary>

```python
class OnInstallHarrixNotesExplorerExtension(ActionBase):

    icon = "📦"
    title = "Update/Install Harrix Notes Explorer (HSK) extension for VSCode"
    cli_available = True
    cli_hint = "dev install-harrix-notes-explorer-hsk vscode"

    _HARRIX_NOTES_EXPLORER_EXT_ID = "local.harrix-notes-explorer-hsk"
    _HARRIX_NOTES_EXPLORER_EXT_UUID = "fbb16925-9395-59b6-ad7f-f25518ab2be8"

    _EDITOR_LABEL_VSCODE = "VS Code"
    _EDITOR_LABEL_INSIDERS = "VS Code Insiders"
    _EDITOR_LABEL_CURSOR = "Cursor"
    _EDITOR_LABEL_VSCODIUM = "VSCodium"
    _EDITOR_LABEL_WINDSURF = "Windsurf"
    _EDITOR_LABEL_ANTIGRAVITY = "Google Antigravity"
    _EDITOR_NOT_INSTALLED_SUFFIX = " (not installed)"
    _SUPPORTED_WIN32_EDITOR_LABELS: tuple[str, ...] = (
        _EDITOR_LABEL_VSCODE,
        _EDITOR_LABEL_INSIDERS,
        _EDITOR_LABEL_CURSOR,
        _EDITOR_LABEL_VSCODIUM,
        _EDITOR_LABEL_WINDSURF,
        _EDITOR_LABEL_ANTIGRAVITY,
    )
    _CLI_EDITOR_TOKEN_TO_LABEL: ClassVar[dict[str, str]] = {
        "vscode": _EDITOR_LABEL_VSCODE,
        "code": _EDITOR_LABEL_VSCODE,
        "insiders": _EDITOR_LABEL_INSIDERS,
        "code-insiders": _EDITOR_LABEL_INSIDERS,
        "cursor": _EDITOR_LABEL_CURSOR,
        "vscodium": _EDITOR_LABEL_VSCODIUM,
        "codium": _EDITOR_LABEL_VSCODIUM,
        "windsurf": _EDITOR_LABEL_WINDSURF,
        "antigravity": _EDITOR_LABEL_ANTIGRAVITY,
    }
    CLI_EDITOR_CHOICES: tuple[str, ...] = (
        "vscode",
        "insiders",
        "cursor",
        "vscodium",
        "windsurf",
        "antigravity",
    )

    @ActionBase.handle_exceptions("install Harrix Notes Explorer (HSK) extension")
    def execute(
        self,
        *_args: Any,
        editor: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Copy extension files into each selected editor's extensions directory."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        ext_dir = (h.dev.get_project_root() / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not ext_dir.is_dir():
            self.add_line(f"❌ Extension folder not found: {ext_dir}")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            if not editor or not str(editor).strip():
                self.add_line("❌ Editor is required (e.g. vscode, insiders, cursor).")
                return
            label = self._resolve_editor_cli_token(str(editor))
            if label is None:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(f'❌ Unknown editor "{editor}". Supported: {supported}.')
                return
            self._install_for_editors([label], ext_dir)
            return

        installed = set(self._discover_win32_editors())
        all_editors = self._all_supported_win32_editor_labels()
        choices = [self._editor_choice_label(e, installed=e in installed) for e in all_editors]
        disabled_choices = [self._editor_choice_label(e, installed=False) for e in all_editors if e not in installed]
        default_selected = [
            self._editor_choice_label(e, installed=True)
            for e in all_editors
            if e in installed and self._is_harrix_notes_explorer_installed(e)
        ]
        selected = self.dialogs.get_checkbox_selection(
            self.title,
            "Install or update Harrix Notes Explorer (HSK) for which editors? "
            "Grayed items are not detected on this system. Unchecked editors are skipped.",
            choices,
            default_selected=default_selected,
            disabled_choices=disabled_choices,
        )
        if not selected:
            self.add_line("Canceled or no editors selected.")
            self.show_result()
            return

        selected_canonical = [self._canonical_editor_label(s) for s in selected]
        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install.")
            self.show_result()
            return

        self._install_for_editors(selected_canonical, ext_dir)
        self.show_result()

    @classmethod
    def _all_supported_win32_editor_labels(cls) -> list[str]:
        """Return display labels for all supported VS Code-family editors (stable order)."""
        return list(cls._SUPPORTED_WIN32_EDITOR_LABELS)

    @staticmethod
    def _antigravity_installed_win32() -> bool:
        if shutil.which("antigravity"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Antigravity" / "Antigravity.exe")
        if pf:
            candidates.append(Path(pf) / "Antigravity" / "Antigravity.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Antigravity" / "Antigravity.exe")
        return any(p.is_file() for p in candidates)

    @classmethod
    def _canonical_editor_label(cls, display: str) -> str:
        """Strip ``(not installed)`` suffix from a dialog choice label."""
        suffix = cls._EDITOR_NOT_INSTALLED_SUFFIX
        if display.endswith(suffix):
            return display[: -len(suffix)]
        return display

    @staticmethod
    def _cursor_installed_win32() -> bool:
        if shutil.which("cursor"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "cursor" / "Cursor.exe")
        if pf:
            candidates.append(Path(pf) / "Cursor" / "Cursor.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Cursor" / "Cursor.exe")
        return any(p.is_file() for p in candidates)

    @classmethod
    def _dest_extension_roots(cls, selected_labels: list[str]) -> list[tuple[str, Path]]:
        """Map selected editor labels to each editor's user ``extensions`` directory."""
        home = Path.home()
        mapping: dict[str, Path] = {
            cls._EDITOR_LABEL_VSCODE: home / ".vscode" / "extensions",
            cls._EDITOR_LABEL_INSIDERS: home / ".vscode-insiders" / "extensions",
            cls._EDITOR_LABEL_CURSOR: home / ".cursor" / "extensions",
            cls._EDITOR_LABEL_VSCODIUM: home / ".vscode-oss" / "extensions",
            cls._EDITOR_LABEL_WINDSURF: home / ".windsurf" / "extensions",
            cls._EDITOR_LABEL_ANTIGRAVITY: home / ".antigravity" / "extensions",
        }
        out: list[tuple[str, Path]] = []
        for label in selected_labels:
            root = mapping.get(label)
            if root is not None:
                out.append((label, root))
        return out

    @classmethod
    def _discover_win32_editors(cls) -> list[str]:
        """Return display labels for detected VS Code-family installs (stable order)."""
        found: list[str] = []
        if cls._vscode_stable_installed_win32():
            found.append(cls._EDITOR_LABEL_VSCODE)
        if cls._vscode_insiders_installed_win32():
            found.append(cls._EDITOR_LABEL_INSIDERS)
        if cls._cursor_installed_win32():
            found.append(cls._EDITOR_LABEL_CURSOR)
        if cls._vscodium_installed_win32():
            found.append(cls._EDITOR_LABEL_VSCODIUM)
        if cls._windsurf_installed_win32():
            found.append(cls._EDITOR_LABEL_WINDSURF)
        if cls._antigravity_installed_win32():
            found.append(cls._EDITOR_LABEL_ANTIGRAVITY)
        return found

    @staticmethod
    def _editor_choice_label(canonical: str, *, installed: bool) -> str:
        """Return dialog checkbox text for *canonical* editor name."""
        if installed:
            return canonical
        return f"{canonical}{OnInstallHarrixNotesExplorerExtension._EDITOR_NOT_INSTALLED_SUFFIX}"

    def _install_for_editors(self, selected_canonical: list[str], ext_dir: Path) -> None:
        """Copy the bundled extension into each editor's extensions directory."""
        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install.")
            return

        ext_version = "0.0.1"
        try:
            with (ext_dir / "package.json").open(encoding="utf-8") as f:
                ext_version = str(json.load(f).get("version", ext_version))
        except (OSError, json.JSONDecodeError, TypeError):
            pass

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        for label, ext_root in dest_pairs:
            dest = ext_root / "harrix-notes-explorer-hsk"
            try:
                ext_root.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=False)
                shutil.copytree(ext_dir, dest, ignore=ignore)
            except OSError as e:
                self.add_line(f"❌ {label}: could not copy to {dest}: {e}")
                self.add_line("   Close that editor if files are locked, then try again.")
                continue
            merged, merge_err = self._merge_harrix_notes_explorer_extensions_json(ext_root, dest, ext_version)
            if merged:
                self.add_line(f"✅ {label}: installed to {dest} (extensions.json updated)")
            else:
                self.add_line(f"✅ {label}: installed to {dest}")
                self.add_line(
                    f"⚠️ {label}: could not update extensions.json ({merge_err}). "
                    "Try Command Palette → Developer: Install Extension from Location, then reload the window."
                )

    @classmethod
    def _is_harrix_notes_explorer_installed(cls, editor_label: str) -> bool:
        """Return whether ``harrix-notes-explorer-hsk`` is present with expected manifest under that editor."""
        pairs = cls._dest_extension_roots([editor_label])
        if not pairs:
            return False
        _, ext_root = pairs[0]
        pkg = ext_root / "harrix-notes-explorer-hsk" / "package.json"
        if not pkg.is_file():
            return False
        try:
            with pkg.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return False
        if not isinstance(data, dict):
            return False
        return str(data.get("name", "")) == "harrix-notes-explorer-hsk" and str(data.get("publisher", "")) == "local"

    @classmethod
    def _merge_harrix_notes_explorer_extensions_json(cls, ext_root: Path, dest: Path, version: str) -> tuple[bool, str]:
        """Upsert ``local.harrix-notes-explorer-hsk`` in ``extensions.json`` under ``ext_root``."""
        json_path = ext_root / "extensions.json"
        data: list[Any]
        try:
            if json_path.is_file():
                loaded = json.loads(json_path.read_text(encoding="utf-8"))
                if not isinstance(loaded, list):
                    return False, "extensions.json root is not a JSON array"
                data = loaded
            else:
                data = []
        except json.JSONDecodeError as e:
            return False, f"invalid JSON ({e})"

        ext_id = cls._HARRIX_NOTES_EXPLORER_EXT_ID
        data = [x for x in data if not (isinstance(x, dict) and x.get("identifier", {}).get("id") == ext_id)]

        uri_path = cls._vscode_extensions_json_uri_path(dest)
        ts = int(time.time() * 1000)
        uuid_val = cls._HARRIX_NOTES_EXPLORER_EXT_UUID
        entry: dict[str, Any] = {
            "identifier": {"id": ext_id, "uuid": uuid_val},
            "version": version,
            "location": {"$mid": 1, "path": uri_path, "scheme": "file"},
            "relativeLocation": dest.name,
            "metadata": {
                "installedTimestamp": ts,
                "pinned": False,
                "source": "path",
                "id": uuid_val,
                "publisherDisplayName": "local",
                "targetPlatform": "undefined",
                "updated": False,
                "private": False,
                "isPreReleaseVersion": False,
                "hasPreReleaseVersion": False,
                "preRelease": False,
            },
        }
        data.append(entry)

        tmp_path = ext_root / f".extensions.json.{os.getpid()}.tmp"
        try:
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            tmp_path.write_text(payload, encoding="utf-8")
            tmp_path.replace(json_path)
        except OSError as e:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)
            return False, str(e)
        return True, ""

    @classmethod
    def _resolve_editor_cli_token(cls, token: str) -> str | None:
        """Map a CLI editor token (and aliases) to a canonical display label."""
        key = str(token).strip().lower()
        if not key:
            return None
        return cls._CLI_EDITOR_TOKEN_TO_LABEL.get(key)

    @staticmethod
    def _vscode_extensions_json_uri_path(folder: Path) -> str:
        """Match VS Code ``extensions.json`` ``location.path`` shape (e.g. ``/c:/Users/...``)."""
        s = folder.resolve().as_posix()
        try:
            if s[1] == ":" and s[0].isalpha():
                return f"/{s[0].lower()}:{s[2:]}"
        except IndexError:
            pass
        return s if s.startswith("/") else f"/{s}"

    @staticmethod
    def _vscode_insiders_installed_win32() -> bool:
        if shutil.which("code-insiders"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        if pf:
            candidates.append(Path(pf) / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        return any(p.is_file() for p in candidates)

    @staticmethod
    def _vscode_stable_installed_win32() -> bool:
        if shutil.which("code"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Microsoft VS Code" / "Code.exe")
        if pf:
            candidates.append(Path(pf) / "Microsoft VS Code" / "Code.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Microsoft VS Code" / "Code.exe")
        return any(p.is_file() for p in candidates)

    @staticmethod
    def _vscodium_installed_win32() -> bool:
        if shutil.which("codium"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "VSCodium" / "VSCodium.exe")
        if pf:
            candidates.append(Path(pf) / "VSCodium" / "VSCodium.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "VSCodium" / "VSCodium.exe")
        return any(p.is_file() for p in candidates)

    @staticmethod
    def _windsurf_installed_win32() -> bool:
        if shutil.which("windsurf"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.extend(
                [
                    Path(local) / "Programs" / "Windsurf" / "Windsurf.exe",
                    Path(local) / "Programs" / "windsurf" / "Windsurf.exe",
                ]
            )
        if pf:
            candidates.extend(
                [
                    Path(pf) / "Windsurf" / "Windsurf.exe",
                    Path(pf) / "windsurf" / "Windsurf.exe",
                ]
            )
        if pfx86:
            candidates.extend(
                [
                    Path(pfx86) / "Windsurf" / "Windsurf.exe",
                    Path(pfx86) / "windsurf" / "Windsurf.exe",
                ]
            )
        return any(p.is_file() for p in candidates)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Copy extension files into each selected editor's extensions directory.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        editor: str | None = None,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        ext_dir = (h.dev.get_project_root() / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not ext_dir.is_dir():
            self.add_line(f"❌ Extension folder not found: {ext_dir}")
            if not noninteractive:
                self.show_result()
            return

        if noninteractive:
            if not editor or not str(editor).strip():
                self.add_line("❌ Editor is required (e.g. vscode, insiders, cursor).")
                return
            label = self._resolve_editor_cli_token(str(editor))
            if label is None:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(f'❌ Unknown editor "{editor}". Supported: {supported}.')
                return
            self._install_for_editors([label], ext_dir)
            return

        installed = set(self._discover_win32_editors())
        all_editors = self._all_supported_win32_editor_labels()
        choices = [self._editor_choice_label(e, installed=e in installed) for e in all_editors]
        disabled_choices = [self._editor_choice_label(e, installed=False) for e in all_editors if e not in installed]
        default_selected = [
            self._editor_choice_label(e, installed=True)
            for e in all_editors
            if e in installed and self._is_harrix_notes_explorer_installed(e)
        ]
        selected = self.dialogs.get_checkbox_selection(
            self.title,
            "Install or update Harrix Notes Explorer (HSK) for which editors? "
            "Grayed items are not detected on this system. Unchecked editors are skipped.",
            choices,
            default_selected=default_selected,
            disabled_choices=disabled_choices,
        )
        if not selected:
            self.add_line("Canceled or no editors selected.")
            self.show_result()
            return

        selected_canonical = [self._canonical_editor_label(s) for s in selected]
        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install.")
            self.show_result()
            return

        self._install_for_editors(selected_canonical, ext_dir)
        self.show_result()
```

</details>

### ⚙️ Method `_all_supported_win32_editor_labels`

```python
def _all_supported_win32_editor_labels(cls) -> list[str]
```

Return display labels for all supported VS Code-family editors (stable order).

<details>
<summary>Code:</summary>

```python
def _all_supported_win32_editor_labels(cls) -> list[str]:
        return list(cls._SUPPORTED_WIN32_EDITOR_LABELS)
```

</details>

### ⚙️ Method `_antigravity_installed_win32`

```python
def _antigravity_installed_win32() -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _antigravity_installed_win32() -> bool:
        if shutil.which("antigravity"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Antigravity" / "Antigravity.exe")
        if pf:
            candidates.append(Path(pf) / "Antigravity" / "Antigravity.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Antigravity" / "Antigravity.exe")
        return any(p.is_file() for p in candidates)
```

</details>

### ⚙️ Method `_canonical_editor_label`

```python
def _canonical_editor_label(cls, display: str) -> str
```

Strip `(not installed)` suffix from a dialog choice label.

<details>
<summary>Code:</summary>

```python
def _canonical_editor_label(cls, display: str) -> str:
        suffix = cls._EDITOR_NOT_INSTALLED_SUFFIX
        if display.endswith(suffix):
            return display[: -len(suffix)]
        return display
```

</details>

### ⚙️ Method `_cursor_installed_win32`

```python
def _cursor_installed_win32() -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _cursor_installed_win32() -> bool:
        if shutil.which("cursor"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "cursor" / "Cursor.exe")
        if pf:
            candidates.append(Path(pf) / "Cursor" / "Cursor.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Cursor" / "Cursor.exe")
        return any(p.is_file() for p in candidates)
```

</details>

### ⚙️ Method `_dest_extension_roots`

```python
def _dest_extension_roots(cls, selected_labels: list[str]) -> list[tuple[str, Path]]
```

Map selected editor labels to each editor's user `extensions` directory.

<details>
<summary>Code:</summary>

```python
def _dest_extension_roots(cls, selected_labels: list[str]) -> list[tuple[str, Path]]:
        home = Path.home()
        mapping: dict[str, Path] = {
            cls._EDITOR_LABEL_VSCODE: home / ".vscode" / "extensions",
            cls._EDITOR_LABEL_INSIDERS: home / ".vscode-insiders" / "extensions",
            cls._EDITOR_LABEL_CURSOR: home / ".cursor" / "extensions",
            cls._EDITOR_LABEL_VSCODIUM: home / ".vscode-oss" / "extensions",
            cls._EDITOR_LABEL_WINDSURF: home / ".windsurf" / "extensions",
            cls._EDITOR_LABEL_ANTIGRAVITY: home / ".antigravity" / "extensions",
        }
        out: list[tuple[str, Path]] = []
        for label in selected_labels:
            root = mapping.get(label)
            if root is not None:
                out.append((label, root))
        return out
```

</details>

### ⚙️ Method `_discover_win32_editors`

```python
def _discover_win32_editors(cls) -> list[str]
```

Return display labels for detected VS Code-family installs (stable order).

<details>
<summary>Code:</summary>

```python
def _discover_win32_editors(cls) -> list[str]:
        found: list[str] = []
        if cls._vscode_stable_installed_win32():
            found.append(cls._EDITOR_LABEL_VSCODE)
        if cls._vscode_insiders_installed_win32():
            found.append(cls._EDITOR_LABEL_INSIDERS)
        if cls._cursor_installed_win32():
            found.append(cls._EDITOR_LABEL_CURSOR)
        if cls._vscodium_installed_win32():
            found.append(cls._EDITOR_LABEL_VSCODIUM)
        if cls._windsurf_installed_win32():
            found.append(cls._EDITOR_LABEL_WINDSURF)
        if cls._antigravity_installed_win32():
            found.append(cls._EDITOR_LABEL_ANTIGRAVITY)
        return found
```

</details>

### ⚙️ Method `_editor_choice_label`

```python
def _editor_choice_label(canonical: str) -> str
```

Return dialog checkbox text for _canonical_ editor name.

<details>
<summary>Code:</summary>

```python
def _editor_choice_label(canonical: str, *, installed: bool) -> str:
        if installed:
            return canonical
        return f"{canonical}{OnInstallHarrixNotesExplorerExtension._EDITOR_NOT_INSTALLED_SUFFIX}"
```

</details>

### ⚙️ Method `_install_for_editors`

```python
def _install_for_editors(self, selected_canonical: list[str], ext_dir: Path) -> None
```

Copy the bundled extension into each editor's extensions directory.

<details>
<summary>Code:</summary>

```python
def _install_for_editors(self, selected_canonical: list[str], ext_dir: Path) -> None:
        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install.")
            return

        ext_version = "0.0.1"
        try:
            with (ext_dir / "package.json").open(encoding="utf-8") as f:
                ext_version = str(json.load(f).get("version", ext_version))
        except (OSError, json.JSONDecodeError, TypeError):
            pass

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        for label, ext_root in dest_pairs:
            dest = ext_root / "harrix-notes-explorer-hsk"
            try:
                ext_root.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=False)
                shutil.copytree(ext_dir, dest, ignore=ignore)
            except OSError as e:
                self.add_line(f"❌ {label}: could not copy to {dest}: {e}")
                self.add_line("   Close that editor if files are locked, then try again.")
                continue
            merged, merge_err = self._merge_harrix_notes_explorer_extensions_json(ext_root, dest, ext_version)
            if merged:
                self.add_line(f"✅ {label}: installed to {dest} (extensions.json updated)")
            else:
                self.add_line(f"✅ {label}: installed to {dest}")
                self.add_line(
                    f"⚠️ {label}: could not update extensions.json ({merge_err}). "
                    "Try Command Palette → Developer: Install Extension from Location, then reload the window."
                )
```

</details>

### ⚙️ Method `_is_harrix_notes_explorer_installed`

```python
def _is_harrix_notes_explorer_installed(cls, editor_label: str) -> bool
```

Return whether `harrix-notes-explorer-hsk` is present with expected manifest under that editor.

<details>
<summary>Code:</summary>

```python
def _is_harrix_notes_explorer_installed(cls, editor_label: str) -> bool:
        pairs = cls._dest_extension_roots([editor_label])
        if not pairs:
            return False
        _, ext_root = pairs[0]
        pkg = ext_root / "harrix-notes-explorer-hsk" / "package.json"
        if not pkg.is_file():
            return False
        try:
            with pkg.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return False
        if not isinstance(data, dict):
            return False
        return str(data.get("name", "")) == "harrix-notes-explorer-hsk" and str(data.get("publisher", "")) == "local"
```

</details>

### ⚙️ Method `_merge_harrix_notes_explorer_extensions_json`

```python
def _merge_harrix_notes_explorer_extensions_json(cls, ext_root: Path, dest: Path, version: str) -> tuple[bool, str]
```

Upsert `local.harrix-notes-explorer-hsk` in `extensions.json` under `ext_root`.

<details>
<summary>Code:</summary>

```python
def _merge_harrix_notes_explorer_extensions_json(cls, ext_root: Path, dest: Path, version: str) -> tuple[bool, str]:
        json_path = ext_root / "extensions.json"
        data: list[Any]
        try:
            if json_path.is_file():
                loaded = json.loads(json_path.read_text(encoding="utf-8"))
                if not isinstance(loaded, list):
                    return False, "extensions.json root is not a JSON array"
                data = loaded
            else:
                data = []
        except json.JSONDecodeError as e:
            return False, f"invalid JSON ({e})"

        ext_id = cls._HARRIX_NOTES_EXPLORER_EXT_ID
        data = [x for x in data if not (isinstance(x, dict) and x.get("identifier", {}).get("id") == ext_id)]

        uri_path = cls._vscode_extensions_json_uri_path(dest)
        ts = int(time.time() * 1000)
        uuid_val = cls._HARRIX_NOTES_EXPLORER_EXT_UUID
        entry: dict[str, Any] = {
            "identifier": {"id": ext_id, "uuid": uuid_val},
            "version": version,
            "location": {"$mid": 1, "path": uri_path, "scheme": "file"},
            "relativeLocation": dest.name,
            "metadata": {
                "installedTimestamp": ts,
                "pinned": False,
                "source": "path",
                "id": uuid_val,
                "publisherDisplayName": "local",
                "targetPlatform": "undefined",
                "updated": False,
                "private": False,
                "isPreReleaseVersion": False,
                "hasPreReleaseVersion": False,
                "preRelease": False,
            },
        }
        data.append(entry)

        tmp_path = ext_root / f".extensions.json.{os.getpid()}.tmp"
        try:
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            tmp_path.write_text(payload, encoding="utf-8")
            tmp_path.replace(json_path)
        except OSError as e:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)
            return False, str(e)
        return True, ""
```

</details>

### ⚙️ Method `_resolve_editor_cli_token`

```python
def _resolve_editor_cli_token(cls, token: str) -> str | None
```

Map a CLI editor token (and aliases) to a canonical display label.

<details>
<summary>Code:</summary>

```python
def _resolve_editor_cli_token(cls, token: str) -> str | None:
        key = str(token).strip().lower()
        if not key:
            return None
        return cls._CLI_EDITOR_TOKEN_TO_LABEL.get(key)
```

</details>

### ⚙️ Method `_vscode_extensions_json_uri_path`

```python
def _vscode_extensions_json_uri_path(folder: Path) -> str
```

Match VS Code `extensions.json` `location.path` shape (e.g. `/c:/Users/...`).

<details>
<summary>Code:</summary>

```python
def _vscode_extensions_json_uri_path(folder: Path) -> str:
        s = folder.resolve().as_posix()
        try:
            if s[1] == ":" and s[0].isalpha():
                return f"/{s[0].lower()}:{s[2:]}"
        except IndexError:
            pass
        return s if s.startswith("/") else f"/{s}"
```

</details>

### ⚙️ Method `_vscode_insiders_installed_win32`

```python
def _vscode_insiders_installed_win32() -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _vscode_insiders_installed_win32() -> bool:
        if shutil.which("code-insiders"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        if pf:
            candidates.append(Path(pf) / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Microsoft VS Code Insiders" / "Code - Insiders.exe")
        return any(p.is_file() for p in candidates)
```

</details>

### ⚙️ Method `_vscode_stable_installed_win32`

```python
def _vscode_stable_installed_win32() -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _vscode_stable_installed_win32() -> bool:
        if shutil.which("code"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "Microsoft VS Code" / "Code.exe")
        if pf:
            candidates.append(Path(pf) / "Microsoft VS Code" / "Code.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "Microsoft VS Code" / "Code.exe")
        return any(p.is_file() for p in candidates)
```

</details>

### ⚙️ Method `_vscodium_installed_win32`

```python
def _vscodium_installed_win32() -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _vscodium_installed_win32() -> bool:
        if shutil.which("codium"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.append(Path(local) / "Programs" / "VSCodium" / "VSCodium.exe")
        if pf:
            candidates.append(Path(pf) / "VSCodium" / "VSCodium.exe")
        if pfx86:
            candidates.append(Path(pfx86) / "VSCodium" / "VSCodium.exe")
        return any(p.is_file() for p in candidates)
```

</details>

### ⚙️ Method `_windsurf_installed_win32`

```python
def _windsurf_installed_win32() -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _windsurf_installed_win32() -> bool:
        if shutil.which("windsurf"):
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        pf = os.environ.get("PROGRAMFILES", "")
        pfx86 = os.environ.get("PROGRAMFILES(X86)", "")
        candidates: list[Path] = []
        if local:
            candidates.extend(
                [
                    Path(local) / "Programs" / "Windsurf" / "Windsurf.exe",
                    Path(local) / "Programs" / "windsurf" / "Windsurf.exe",
                ]
            )
        if pf:
            candidates.extend(
                [
                    Path(pf) / "Windsurf" / "Windsurf.exe",
                    Path(pf) / "windsurf" / "Windsurf.exe",
                ]
            )
        if pfx86:
            candidates.extend(
                [
                    Path(pfx86) / "Windsurf" / "Windsurf.exe",
                    Path(pfx86) / "windsurf" / "Windsurf.exe",
                ]
            )
        return any(p.is_file() for p in candidates)
```

</details>
