"""Actions for Python development and code management."""

from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, ClassVar, cast

import harrix_pylib as h

from harrix_swiss_knife.actions.base import ActionBase


class OnInstallHarrixNotesExplorerExtension(ActionBase):
    """Build/sync public Harrix Notes Explorer, install HSK, optionally install public into editors.

    On Windows: builds the public extension from ``vscode/harrix-notes-explorer-hsk`` into
    ``path_harrix_notes_explorer`` (git repo, keeps ``.git/``), copies HSK into each selected
    editor profile, and optionally copies the public ``harrix-notes-explorer`` tree from that repo.
    """

    icon = "📦"
    title = "Update/Install Harrix Notes Explorer extensions for VSCode…"
    cli_available = True
    cli_hint = "dev install-harrix-notes-explorer-hsk vscode [--with-public]"

    _HARRIX_NOTES_EXPLORER_EXT_ID = "local.harrix-notes-explorer-hsk"
    _HARRIX_NOTES_EXPLORER_EXT_UUID = "fbb16925-9395-59b6-ad7f-f25518ab2be8"
    _PUBLIC_EXT_FOLDER = "harrix-notes-explorer"
    _PUBLIC_EXT_DEFAULT_UUID = "c8e4a1f2-6b3d-4e9a-8f1c-2d5e7a9b0c3d"

    _TEXT_SUFFIXES: ClassVar[frozenset[str]] = frozenset({".js", ".json", ".md", ".css"})
    _CLI_FILES: ClassVar[frozenset[str]] = frozenset(
        {
            "harrix-cli.js",
            "HARRIX_CLI.md",
            "package.harrix-cli.contributes.json",
        }
    )
    _HSK_TO_PUBLIC_REPLACEMENTS: ClassVar[tuple[tuple[str, str], ...]] = (
        ("Harrix Notes Explorer (HSK)", "Harrix Notes Explorer"),
        ("Refresh Harrix Notes (HSK)", "Refresh Harrix Notes"),
        ("Harrix Notes (HSK)", "Harrix Notes"),
        ("Harrix Notes HSK", "Harrix Notes"),
        ("harrix-notes-explorer-hsk", "harrix-notes-explorer"),
        ("harrixNotesExplorerHsk", "harrixNotesExplorer"),
        ("gFileHsk", "gFile"),
    )

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

        public_repo = self._resolve_public_repo_path()
        publisher = self._resolve_public_publisher()

        if public_repo is not None:
            if not self._sync_public_repo(public_repo, hsk_dir, project_root, publisher):
                if not noninteractive:
                    self.show_result()
                return
        else:
            self.add_line(
                "⚠️ path_harrix_notes_explorer is empty; skipped public repo sync. "
                "Set it in config/config.json to publish the public build."
            )

        if noninteractive:
            if not editor or not str(editor).strip():
                self.add_line("❌ Editor is required (e.g. vscode, insiders, cursor).")
                return
            label = self._resolve_editor_cli_token(str(editor))
            if label is None:
                supported = ", ".join(self.CLI_EDITOR_CHOICES)
                self.add_line(f'❌ Unknown editor "{editor}". Supported: {supported}.')
                return
            selected_canonical = [label]
        else:
            selected_canonical = self._select_editors_interactive()
            if not selected_canonical:
                if not self.result_lines:
                    self.add_line("Canceled or no editors selected.")
                self.show_result()
                return

        self._install_hsk_for_editors(selected_canonical, hsk_dir)

        install_public = with_public
        if not noninteractive and public_repo is not None:
            default_yes = any(self._is_public_extension_installed(e, publisher) for e in selected_canonical)
            install_public = self.get_yes_no_question(
                self.title,
                "Also install public Harrix Notes Explorer (harrix-notes-explorer) "
                "to the same editors from the synced repo?",
                default_yes=default_yes,
            )
        elif with_public:
            if public_repo is None:
                self.add_line("❌ --with-public requires path_harrix_notes_explorer in config.")
                if not noninteractive:
                    self.show_result()
                return
            install_public = True

        if install_public and public_repo is not None:
            self._install_public_for_editors(selected_canonical, public_repo)

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
    def _apply_hsk_to_public_renames(cls, text: str, *, publisher: str) -> str:
        for old, new in cls._HSK_TO_PUBLIC_REPLACEMENTS:
            text = text.replace(old, new)
        return re.sub(r'"publisher"\s*:\s*"local"', f'"publisher": "{publisher}"', text)

    @classmethod
    def _build_public_extension(cls, source_dir: Path, *, publisher: str) -> Path:
        """Copy *source_dir* to a temp folder, transform to public build, return temp path."""
        source_dir = source_dir.resolve()
        if not source_dir.is_dir():
            msg = f"Extension source not found: {source_dir}"
            raise FileNotFoundError(msg)

        build_dir = Path(tempfile.mkdtemp(prefix="harrix-notes-explorer-public-"))
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
        shutil.copytree(source_dir, build_dir, ignore=ignore, dirs_exist_ok=True)

        manifest_path = build_dir / "package.harrix-cli.contributes.json"
        manifest: dict[str, Any] = {}
        if manifest_path.is_file():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        for path in sorted(build_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.name in cls._CLI_FILES:
                path.unlink()
                continue
            if path.suffix.lower() not in cls._TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8")
            if path.name == "package.json":
                data = json.loads(text)
                data = cls._strip_cli_from_package_json(data, manifest)
                data["publisher"] = publisher
                data["description"] = cls._public_description(str(data.get("description", "")))
                text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
                text = cls._apply_hsk_to_public_renames(text, publisher=publisher)
            elif path.name == "extension.js":
                text = cls._patch_extension_js(text)
                text = cls._apply_hsk_to_public_renames(text, publisher=publisher)
            else:
                text = cls._apply_hsk_to_public_renames(text, publisher=publisher)
            path.write_text(text, encoding="utf-8", newline="\n")

        return build_dir

    @classmethod
    def _canonical_editor_label(cls, display: str) -> str:
        """Strip ``(not installed)`` suffix from a dialog choice label."""
        suffix = cls._EDITOR_NOT_INSTALLED_SUFFIX
        if display.endswith(suffix):
            return display[: -len(suffix)]
        return display

    @staticmethod
    def _cleanup_build_dir(build_dir: Path) -> None:
        if build_dir.is_dir():
            shutil.rmtree(build_dir, ignore_errors=True)

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

    @classmethod
    def _existing_extension_uuid(cls, ext_root: Path, ext_id: str) -> str | None:
        """Return UUID from an existing ``extensions.json`` entry for *ext_id*, if any."""
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

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
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

        ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
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
        """Return whether ``harrix-notes-explorer-hsk`` is present with expected manifest."""
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
    def _is_public_extension_installed(cls, editor_label: str, publisher: str) -> bool:
        """Return whether public ``harrix-notes-explorer`` is installed for *publisher*."""
        pairs = cls._dest_extension_roots([editor_label])
        if not pairs:
            return False
        _, ext_root = pairs[0]
        pkg = ext_root / cls._PUBLIC_EXT_FOLDER / "package.json"
        if not pkg.is_file():
            return False
        try:
            with pkg.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, TypeError):
            return False
        if not isinstance(data, dict):
            return False
        return str(data.get("name", "")) == cls._PUBLIC_EXT_FOLDER and str(data.get("publisher", "")) == publisher

    @staticmethod
    def _item_command_in_set(item: object, command_ids: set[str]) -> bool:
        if not isinstance(item, dict):
            return False
        command = cast("dict[str, Any]", item).get("command")
        return isinstance(command, str) and command in command_ids

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
        """Upsert one extension entry in ``extensions.json`` under ``ext_root``."""
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
        """Upsert ``local.harrix-notes-explorer-hsk`` in ``extensions.json``."""
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
        """Upsert ``{publisher}.harrix-notes-explorer`` in ``extensions.json``."""
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
    def _patch_extension_js(cls, content: str) -> str:
        content = re.sub(
            r"/\*\* harrix-swiss-knife-cli integration.*?\*/\s*",
            "",
            content,
            count=1,
            flags=re.DOTALL,
        )
        content = re.sub(r"const harrixCli = require\('\./harrix-cli'\);\s*\n", "", content)

        content = re.sub(
            r"\s*\|\|\s*harrixCli\.folderListedWithoutMarkdown\(\s*e\.name,\s*"
            r"this\.getTemplatesForFolder\(path\.join\(dir, e\.name\)\)\.length\s*\)",
            "",
            content,
        )

        content = re.sub(
            r"\s*\|\|\s*harrixCli\.isSpecialNotesFolderName\(e\.name\)",
            "",
            content,
        )

        content = re.sub(
            r"item\.contextValue = harrixCli\.resolveNotesFolderContextValue\(\{[^}]+\}\);",
            "item.contextValue = hasMergedNoteFs(folderPath, name) ? 'notesFolderWithMerged' : 'notesFolder';",
            content,
            flags=re.DOTALL,
        )

        content = re.sub(
            r"\s*harrixCli\.activateHarrixCliIntegration\(\{[\s\S]*?\}\);\s*\n",
            "\n",
            content,
            count=1,
        )

        content = re.sub(
            r"\s*/\*\* @type \{Map<string, Array<\{id: string, title: string\}>>\} CLI template targets.*?\*/\s*"
            r"this\._templateTargets = new Map\(\);\s*",
            "",
            content,
            flags=re.DOTALL,
        )

        content = re.sub(
            r"\s*/\*\* @param \{Map<string, Array<\{id: string, title: string\}>>\} map \*/\s*"
            r"setTemplateTargets\(map\) \{[\s\S]*?\}\s*",
            "",
            content,
            count=1,
        )

        content = re.sub(
            r"\s*getTemplatesForFolder\(folderPath\) \{[\s\S]*?\}\s*",
            "",
            content,
            count=1,
        )

        content = re.sub(
            r"\s*item\.templateItems = this\.getTemplatesForFolder\(folderPath\);\s*\n",
            "\n",
            content,
        )

        content = re.sub(
            r"(item\.folderDepth = depth;)\s*(item\.contextValue)",
            r"\1\n    \2",
            content,
        )

        if "harrixCli" in content:
            msg = "extension.js still references harrixCli after public build patch"
            raise ValueError(msg)

        return content

    @staticmethod
    def _public_description(description: str) -> str:
        desc = description.strip()
        desc = re.sub(r"\s*—\s*notes panel.*", "", desc, flags=re.IGNORECASE)
        desc = re.sub(r"\s*with harrix-swiss-knife-cli integration\s*", "", desc, flags=re.IGNORECASE)
        desc = desc.strip(" —")
        if not desc or desc == "Harrix Notes Explorer":
            return "Harrix Notes Explorer — custom notes panel for markdown notes"
        if "harrix-swiss-knife-cli" in desc.lower():
            return "Harrix Notes Explorer — custom notes panel for markdown notes"
        return desc

    @classmethod
    def _public_extension_id(cls, publisher: str) -> str:
        return f"{publisher}.{cls._PUBLIC_EXT_FOLDER}"

    @classmethod
    def _read_public_package_meta(cls, public_repo: Path) -> tuple[str, str, str] | None:
        """Return (publisher, name, version) from public repo ``package.json``."""
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

    def _resolve_public_publisher(self) -> str:
        publisher_raw = self.config.get("harrix_notes_explorer_publisher")
        publisher = str(publisher_raw or "").strip()
        if not publisher:
            publisher = str(self.config.get("github_user") or "Harrix").strip().lower() or "harrix"
        return publisher

    def _resolve_public_repo_path(self) -> Path | None:
        dest_raw = self.resolve_config_value(
            "path_harrix_notes_explorer",
            self.config.get("path_harrix_notes_explorer"),
        )
        dest_str = str(dest_raw or "").strip()
        if not dest_str:
            return None
        return Path(dest_str).expanduser()

    def _select_editors_interactive(self) -> list[str]:
        """Show checkbox dialog; return canonical editor labels or empty if canceled."""
        installed = set(self._discover_win32_editors())
        all_editors = self._all_supported_win32_editor_labels()
        choices = [self._editor_choice_label(e, installed=e in installed) for e in all_editors]
        disabled_choices = [self._editor_choice_label(e, installed=False) for e in all_editors if e not in installed]
        default_selected = [
            self._editor_choice_label(e, installed=True)
            for e in all_editors
            if e in installed and self._is_hsk_extension_installed(e)
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
            return []
        selected_canonical = [self._canonical_editor_label(s) for s in selected]
        if not self._dest_extension_roots(selected_canonical):
            self.add_line("❌ No valid editor selection to install.")
            return []
        return selected_canonical

    @classmethod
    def _strip_cli_from_package_json(cls, data: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
        data.pop("_harrixCli", None)

        command_ids = set(manifest.get("commandIds") or [])
        config_keys = set(manifest.get("configurationPropertyKeys") or [])

        contributes = data.get("contributes")
        if isinstance(contributes, dict):
            configuration = contributes.get("configuration")
            if isinstance(configuration, dict):
                props = configuration.get("properties")
                if isinstance(props, dict):
                    for key in config_keys:
                        props.pop(key, None)

            commands = contributes.get("commands")
            if isinstance(commands, list):
                contributes["commands"] = [cmd for cmd in commands if not cls._item_command_in_set(cmd, command_ids)]

            menus = contributes.get("menus")
            if isinstance(menus, dict):
                for menu_key, entries in list(menus.items()):
                    if not isinstance(entries, list):
                        continue
                    menus[menu_key] = [entry for entry in entries if not cls._item_command_in_set(entry, command_ids)]

        return data

    def _sync_public_repo(
        self,
        dest: Path,
        source: Path,
        project_root: Path,
        publisher: str,
    ) -> bool:
        """Build public extension and sync into *dest*; return False on fatal error."""
        if dest.resolve() == project_root:
            self.add_line(f"❌ Refusing to sync into harrix-swiss-knife project root: {dest}")
            return False

        self.add_line(f"Public build source: {source}")
        self.add_line(f"Public repo: {dest}")
        self.add_line(f"Publisher: {publisher}")

        build_dir: Path | None = None
        try:
            build_dir = self._build_public_extension(source, publisher=publisher)
            for line in self._sync_to_repo(build_dir, dest, project_root=project_root):
                self.add_line(line)
                if line.strip().startswith("❌"):
                    return False
        except (OSError, ValueError, json.JSONDecodeError) as e:
            self.add_line(f"❌ Public build failed: {e}")
            return False
        finally:
            if build_dir is not None:
                self._cleanup_build_dir(build_dir)
        return True

    @classmethod
    def _sync_to_repo(cls, build_dir: Path, repo_root: Path, *, project_root: Path | None = None) -> list[str]:
        """Replace *repo_root* contents (except ``.git``) with *build_dir*; return log lines."""
        build_dir = build_dir.resolve()
        repo_root = repo_root.resolve()
        lines: list[str] = []

        if not build_dir.is_dir():
            lines.append(f"❌ Build directory not found: {build_dir}")
            return lines

        if project_root is not None and repo_root == project_root.resolve():
            lines.append(f"❌ Refusing to sync into harrix-swiss-knife project root: {repo_root}")
            return lines

        repo_root.mkdir(parents=True, exist_ok=True)
        if not (repo_root / ".git").is_dir():
            lines.append(f"⚠️ No .git directory under {repo_root} (continuing anyway).")

        removed: list[str] = []
        for entry in repo_root.iterdir():
            if entry.name == ".git":
                continue
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
            removed.append(entry.name)

        for item in build_dir.iterdir():
            dest = repo_root / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        lines.append(f"Removed {len(removed)} item(s) from {repo_root} (kept .git).")
        copied = [p.name for p in build_dir.iterdir()]
        lines.append(f"Copied {len(copied)} item(s): {', '.join(sorted(copied))}.")
        lines.append(f"✅ Public extension synced to {repo_root}")
        return lines

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
