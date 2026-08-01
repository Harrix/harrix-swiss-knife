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

</details>

## 🏛️ Class `OnInstallHarrixNotesExplorerExtension`

```python
class OnInstallHarrixNotesExplorerExtension(ActionBase)
```

Install the Harrix Notes Explorer extension into selected VS Code-like editors.

On Windows: runs `OnSyncHarrixNotesExplorer` (HSK → `path_harrix_notes_explorer`), copies the
HSK extension into each selected editor profile, clears matching `.obsolete` uninstall markers,
and optionally copies the public `harrix-notes-explorer` tree from that repo.

<details>
<summary>Code:</summary>

```python
class OnInstallHarrixNotesExplorerExtension(ActionBase):

    icon = "📦"
    title = "Update/install Harrix Notes Explorer extension for VS Code…"
    cli_available = True
    cli_hint = "dev install-harrix-notes-explorer-hsk vscode [--with-public]"

    _HARRIX_NOTES_EXPLORER_EXT_ID = "local.harrix-notes-explorer-hsk"
    _HARRIX_NOTES_EXPLORER_EXT_UUID = "fbb16925-9395-59b6-ad7f-f25518ab2be8"
    _PUBLIC_EXT_FOLDER = "harrix-notes-explorer"
    _PUBLIC_EXT_DEFAULT_UUID = "c8e4a1f2-6b3d-4e9a-8f1c-2d5e7a9b0c3d"

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

    @ActionBase.handle_exceptions("install Harrix Notes Explorer extensions")
    def execute(
        self,
        *_args: Any,
        editor: str | None = None,
        noninteractive: bool = False,
        with_public: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Sync public repo, install HSK, and optionally install public extension into editors."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        project_root = h.dev.get_project_root().resolve()
        hsk_dir = (project_root / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not hsk_dir.is_dir():
            self.add_line(f"❌ HSK extension folder not found: {hsk_dir}")
            if not noninteractive:
                self.show_result()
            return

        sync_action = OnSyncHarrixNotesExplorer()
        if not sync_action.sync_public_repo():
            for line in sync_action.result_lines:
                self.add_line(str(line))
            if not noninteractive:
                self.show_result()
            return
        for line in sync_action.result_lines:
            self.add_line(str(line))

        public_repo = sync_action.resolve_public_repo_path()

        if noninteractive:
            if not editor or not str(editor).strip():
                self.add_line("❌ Editor is required (e.g. vscode, insiders, cursor).")
                return
            label = self._resolve_editor_cli_token(str(editor))
            if label is None:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(f'❌ Unknown editor "{editor}". Supported: {supported}.')
                return
            selected_hsk = [label]
            selected_public: list[str] = [label] if with_public else []
        else:
            selection = self._select_editors_interactive(offer_public=public_repo is not None)
            if selection is None:
                if not self.result_lines:
                    self.add_line("Canceled or no editors selected.")
                self.show_result()
                return
            selected_hsk, selected_public = selection

        if selected_hsk:
            self._install_hsk_for_editors(selected_hsk, hsk_dir)
        elif noninteractive:
            self.add_line("❌ No editors selected for HSK install.")
            return

        if selected_public:
            if public_repo is None:
                self.add_line("❌ Installing public extension requires path_harrix_notes_explorer in config.")
                if not noninteractive:
                    self.show_result()
                return
            self._install_public_for_editors(selected_public, public_repo)

        if public_repo is not None:
            self.add_line("Commit and push changes in the public repo when ready.")
        if not noninteractive:
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
        """Strip `(not installed)` suffix from a dialog choice label."""
        suffix = cls._EDITOR_NOT_INSTALLED_SUFFIX
        if display.endswith(suffix):
            return display[: -len(suffix)]
        return display

    @classmethod
    def _clear_obsolete_extension(cls, ext_root: Path, ext_id: str, version: str) -> None:
        """Remove uninstall markers for `ext_id` from `ext_root/.obsolete` if present.

        VS Code / Cursor write `{publisher.name}-{version}: true` into `.obsolete` when the user
        uninstalls an extension in the UI. Copying the folder and updating `extensions.json` alone
        does not clear that marker, so the extension stays hidden until `.obsolete` is updated.

        """
        obsolete_path = ext_root / ".obsolete"
        if not obsolete_path.is_file():
            return
        try:
            loaded = json.loads(obsolete_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(loaded, dict):
            return

        exact_key = f"{ext_id}-{version}"
        keys_to_drop = [k for k in loaded if isinstance(k, str) and (k == exact_key or k.startswith(f"{ext_id}-"))]
        if not keys_to_drop:
            return
        for key in keys_to_drop:
            loaded.pop(key, None)

        tmp_path = ext_root / f".obsolete.{os.getpid()}.tmp"
        try:
            payload = json.dumps(loaded, ensure_ascii=False, separators=(",", ":"))
            tmp_path.write_text(payload, encoding="utf-8")
            tmp_path.replace(obsolete_path)
        except OSError:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)

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
        """Map selected editor labels to each editor's user `extensions` directory."""
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
        """Return dialog checkbox text for `canonical` editor name."""
        if installed:
            return canonical
        return f"{canonical}{OnInstallHarrixNotesExplorerExtension._EDITOR_NOT_INSTALLED_SUFFIX}"

    @classmethod
    def _existing_extension_uuid(cls, ext_root: Path, ext_id: str) -> str | None:
        """Return UUID from an existing `extensions.json` entry for `ext_id`, if any."""
        json_path = ext_root / "extensions.json"
        if not json_path.is_file():
            return None
        try:
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if not isinstance(loaded, list):
            return None
        for item in loaded:
            if not isinstance(item, dict):
                continue
            ident = item.get("identifier")
            if isinstance(ident, dict) and ident.get("id") == ext_id:
                uuid_val = ident.get("uuid")
                if isinstance(uuid_val, str) and uuid_val.strip():
                    return uuid_val.strip()
        return None

    def _install_hsk_for_editors(self, selected_canonical: list[str], ext_dir: Path) -> None:
        """Copy the bundled HSK extension into each editor's extensions directory."""
        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install HSK.")
            return

        ext_version = "0.0.1"
        try:
            with (ext_dir / "package.json").open(encoding="utf-8") as f:
                ext_version = str(json.load(f).get("version", ext_version))
        except (OSError, json.JSONDecodeError, TypeError):
            pass

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", ".biome")
        for label, ext_root in dest_pairs:
            dest = ext_root / "harrix-notes-explorer-hsk"
            try:
                ext_root.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=False)
                shutil.copytree(ext_dir, dest, ignore=ignore)
            except OSError as e:
                self.add_line(f"❌ {label}: could not copy HSK to {dest}: {e}")
                self.add_line("   Close that editor if files are locked, then try again.")
                continue
            self._clear_obsolete_extension(ext_root, self._HARRIX_NOTES_EXPLORER_EXT_ID, ext_version)
            merged, merge_err = self._merge_hsk_extensions_json(ext_root, dest, ext_version)
            if merged:
                self.add_line(f"✅ {label}: HSK installed to {dest} (extensions.json updated)")
            else:
                self.add_line(f"✅ {label}: HSK installed to {dest}")
                self.add_line(
                    f"⚠️ {label}: could not update extensions.json ({merge_err}). "
                    "Try Command Palette → Developer: Install Extension from Location, then reload the window."
                )

    def _install_public_for_editors(
        self,
        selected_canonical: list[str],
        public_repo: Path,
    ) -> None:
        """Copy public extension from synced repo into each editor's extensions directory."""
        public_repo = public_repo.resolve()
        if not public_repo.is_dir():
            self.add_line(f"❌ Public extension repo not found: {public_repo}")
            return
        meta = self._read_public_package_meta(public_repo)
        if meta is None:
            self.add_line(f"❌ Invalid or missing package.json in {public_repo}")
            return
        pkg_publisher, pkg_name, ext_version = meta
        if pkg_name != self._PUBLIC_EXT_FOLDER:
            self.add_line(f"⚠️ Expected package name {self._PUBLIC_EXT_FOLDER!r}, got {pkg_name!r}; continuing.")

        dest_pairs = self._dest_extension_roots(selected_canonical)
        if not dest_pairs:
            self.add_line("❌ No valid editor selection to install public extension.")
            return

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", ".biome")
        for label, ext_root in dest_pairs:
            dest = ext_root / self._PUBLIC_EXT_FOLDER
            try:
                ext_root.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    shutil.rmtree(dest, ignore_errors=False)
                shutil.copytree(public_repo, dest, ignore=ignore)
            except OSError as e:
                self.add_line(f"❌ {label}: could not copy public extension to {dest}: {e}")
                self.add_line("   Close that editor if files are locked, then try again.")
                continue
            self._clear_obsolete_extension(ext_root, self._public_extension_id(pkg_publisher), ext_version)
            merged, merge_err = self._merge_public_extensions_json(
                ext_root,
                dest,
                ext_version,
                publisher=pkg_publisher,
            )
            if merged:
                self.add_line(f"✅ {label}: public extension installed to {dest} (extensions.json updated)")
            else:
                self.add_line(f"✅ {label}: public extension installed to {dest}")
                self.add_line(
                    f"⚠️ {label}: could not update extensions.json ({merge_err}). "
                    "Try Command Palette → Developer: Install Extension from Location, then reload the window."
                )

    @classmethod
    def _is_hsk_extension_installed(cls, editor_label: str) -> bool:
        """Return whether `harrix-notes-explorer-hsk` is present with expected manifest."""
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
    def _merge_extensions_json_entry(
        cls,
        ext_root: Path,
        dest: Path,
        version: str,
        *,
        ext_id: str,
        uuid_val: str,
        publisher_display_name: str,
    ) -> tuple[bool, str]:
        """Upsert one extension entry in `extensions.json` under `ext_root`."""
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

        data = [x for x in data if not (isinstance(x, dict) and x.get("identifier", {}).get("id") == ext_id)]

        uri_path = cls._vscode_extensions_json_uri_path(dest)
        ts = int(time.time() * 1000)
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
                "publisherDisplayName": publisher_display_name,
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
    def _merge_hsk_extensions_json(cls, ext_root: Path, dest: Path, version: str) -> tuple[bool, str]:
        """Upsert `local.harrix-notes-explorer-hsk` in `extensions.json`."""
        return cls._merge_extensions_json_entry(
            ext_root,
            dest,
            version,
            ext_id=cls._HARRIX_NOTES_EXPLORER_EXT_ID,
            uuid_val=cls._HARRIX_NOTES_EXPLORER_EXT_UUID,
            publisher_display_name="local",
        )

    @classmethod
    def _merge_public_extensions_json(
        cls,
        ext_root: Path,
        dest: Path,
        version: str,
        *,
        publisher: str,
    ) -> tuple[bool, str]:
        """Upsert `{publisher}.harrix-notes-explorer` in `extensions.json`."""
        ext_id = cls._public_extension_id(publisher)
        uuid_val = cls._existing_extension_uuid(ext_root, ext_id) or cls._PUBLIC_EXT_DEFAULT_UUID
        return cls._merge_extensions_json_entry(
            ext_root,
            dest,
            version,
            ext_id=ext_id,
            uuid_val=uuid_val,
            publisher_display_name=publisher,
        )

    @classmethod
    def _public_extension_id(cls, publisher: str) -> str:
        return f"{publisher}.{cls._PUBLIC_EXT_FOLDER}"

    @classmethod
    def _read_public_package_meta(cls, public_repo: Path) -> tuple[str, str, str] | None:
        """Return (publisher, name, version) from public repo `package.json`."""
        pkg = public_repo / "package.json"
        if not pkg.is_file():
            return None
        try:
            with pkg.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return None
        if not isinstance(data, dict):
            return None
        publisher = str(data.get("publisher", "")).strip()
        name = str(data.get("name", "")).strip()
        version = str(data.get("version", "0.0.1")).strip() or "0.0.1"
        if not publisher or not name:
            return None
        return publisher, name, version

    @classmethod
    def _resolve_editor_cli_token(cls, token: str) -> str | None:
        """Map a CLI editor token (and aliases) to a canonical display label."""
        key = str(token).strip().lower()
        if not key:
            return None
        return cls._CLI_EDITOR_TOKEN_TO_LABEL.get(key)

    def _select_editors_interactive(self, *, offer_public: bool) -> tuple[list[str], list[str]] | None:
        """Show editor checkbox dialog; return (HSK labels, public labels) or `None` if canceled."""
        installed = set(self._discover_win32_editors())
        all_editors = self._all_supported_win32_editor_labels()
        choices = [self._editor_choice_label(e, installed=e in installed) for e in all_editors]
        disabled_choices = [self._editor_choice_label(e, installed=False) for e in all_editors if e not in installed]
        default_hsk = [
            self._editor_choice_label(e, installed=True)
            for e in all_editors
            if e in installed and self._is_hsk_extension_installed(e)
        ]

        if offer_public:
            selected = self.dialogs.get_dual_checkbox_selection(
                self.title,
                section1_title="Harrix Notes Explorer (HSK)",
                section1_label=(
                    "Install or update the HSK extension for which editors? "
                    "Grayed items are not detected on this system. Unchecked editors are skipped."
                ),
                section1_choices=choices,
                section1_default_selected=default_hsk,
                section1_disabled_choices=disabled_choices,
                section2_title="Harrix Notes Explorer (public)",
                section2_label=(
                    "Install or update the public harrix-notes-explorer extension for which editors? "
                    "Same list as above; all unchecked by default. Grayed items are not detected."
                ),
                section2_choices=choices,
                section2_default_selected=[],
                section2_disabled_choices=disabled_choices,
            )
            if selected is None:
                return None
            selected_hsk_raw, selected_public_raw = selected
        else:
            selected_hsk_raw = self.dialogs.get_checkbox_selection(
                self.title,
                "Install or update Harrix Notes Explorer (HSK) for which editors? "
                "Grayed items are not detected on this system. Unchecked editors are skipped.",
                choices,
                default_selected=default_hsk,
                disabled_choices=disabled_choices,
            )
            if not selected_hsk_raw:
                return None
            selected_public_raw = []

        selected_hsk = [self._canonical_editor_label(s) for s in selected_hsk_raw]
        selected_public = [self._canonical_editor_label(s) for s in selected_public_raw]

        if selected_hsk and not self._dest_extension_roots(selected_hsk):
            self.add_line("❌ No valid editor selection for HSK install.")
            return None
        if selected_public and not self._dest_extension_roots(selected_public):
            self.add_line("❌ No valid editor selection for public extension install.")
            return None
        return selected_hsk, selected_public

    @staticmethod
    def _vscode_extensions_json_uri_path(folder: Path) -> str:
        """Match VS Code `extensions.json` `location.path` shape (e.g. `/c:/Users/...`)."""
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

Sync public repo, install HSK, and optionally install public extension into editors.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        editor: str | None = None,
        noninteractive: bool = False,
        with_public: bool = False,
        **_kwargs: Any,
    ) -> None:
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            if not noninteractive:
                self.show_result()
            return

        project_root = h.dev.get_project_root().resolve()
        hsk_dir = (project_root / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not hsk_dir.is_dir():
            self.add_line(f"❌ HSK extension folder not found: {hsk_dir}")
            if not noninteractive:
                self.show_result()
            return

        sync_action = OnSyncHarrixNotesExplorer()
        if not sync_action.sync_public_repo():
            for line in sync_action.result_lines:
                self.add_line(str(line))
            if not noninteractive:
                self.show_result()
            return
        for line in sync_action.result_lines:
            self.add_line(str(line))

        public_repo = sync_action.resolve_public_repo_path()

        if noninteractive:
            if not editor or not str(editor).strip():
                self.add_line("❌ Editor is required (e.g. vscode, insiders, cursor).")
                return
            label = self._resolve_editor_cli_token(str(editor))
            if label is None:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(f'❌ Unknown editor "{editor}". Supported: {supported}.')
                return
            selected_hsk = [label]
            selected_public: list[str] = [label] if with_public else []
        else:
            selection = self._select_editors_interactive(offer_public=public_repo is not None)
            if selection is None:
                if not self.result_lines:
                    self.add_line("Canceled or no editors selected.")
                self.show_result()
                return
            selected_hsk, selected_public = selection

        if selected_hsk:
            self._install_hsk_for_editors(selected_hsk, hsk_dir)
        elif noninteractive:
            self.add_line("❌ No editors selected for HSK install.")
            return

        if selected_public:
            if public_repo is None:
                self.add_line("❌ Installing public extension requires path_harrix_notes_explorer in config.")
                if not noninteractive:
                    self.show_result()
                return
            self._install_public_for_editors(selected_public, public_repo)

        if public_repo is not None:
            self.add_line("Commit and push changes in the public repo when ready.")
        if not noninteractive:
            self.show_result()
```

</details>
