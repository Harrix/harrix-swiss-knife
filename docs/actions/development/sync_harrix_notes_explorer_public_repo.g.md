---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sync_harrix_notes_explorer_public_repo.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSyncHarrixNotesExplorerPublicRepo`](#%EF%B8%8F-class-onsyncharrixnotesexplorerpublicrepo)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `_apply_hsk_to_public_renames`](#%EF%B8%8F-method-_apply_hsk_to_public_renames)
  - [⚙️ Method `_build_public_extension`](#%EF%B8%8F-method-_build_public_extension)
  - [⚙️ Method `_cleanup_build_dir`](#%EF%B8%8F-method-_cleanup_build_dir)
  - [⚙️ Method `_patch_extension_js`](#%EF%B8%8F-method-_patch_extension_js)
  - [⚙️ Method `_public_description`](#%EF%B8%8F-method-_public_description)
  - [⚙️ Method `_strip_cli_from_package_json`](#%EF%B8%8F-method-_strip_cli_from_package_json)
  - [⚙️ Method `_sync_to_repo`](#%EF%B8%8F-method-_sync_to_repo)

</details>

## 🏛️ Class `OnSyncHarrixNotesExplorerPublicRepo`

```python
class OnSyncHarrixNotesExplorerPublicRepo(ActionBase)
```

Build public Harrix Notes Explorer from the HSK extension and sync to a git repo.

Reads `path_harrix_notes_explorer` from config. Deletes everything in that repo except
`.git/`, then copies the transformed extension (no harrix-swiss-knife-cli layer).

<details>
<summary>Code:</summary>

```python
class OnSyncHarrixNotesExplorerPublicRepo(ActionBase):

    icon = "📤"
    title = "Sync Harrix Notes Explorer to public repo"
    cli_available = True
    cli_hint = "dev sync-harrix-notes-explorer --yes"

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

    @ActionBase.handle_exceptions("sync Harrix Notes Explorer public repo")
    def execute(
        self,
        *_args: Any,
        yes: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        """Build and sync the public extension tree into the configured repository."""
        dest_raw = self.resolve_config_value(
            "path_harrix_notes_explorer",
            self.config.get("path_harrix_notes_explorer"),
        )
        dest_str = str(dest_raw or "").strip()
        if not dest_str:
            self.add_line("❌ path_harrix_notes_explorer is empty. Set it in config/config.json.")
            if not noninteractive:
                self.show_result()
            return

        dest = Path(dest_str).expanduser()
        project_root = h.dev.get_project_root().resolve()
        if dest.resolve() == project_root:
            self.add_line(f"❌ Refusing to sync into harrix-swiss-knife project root: {dest}")
            if not noninteractive:
                self.show_result()
            return

        publisher_raw = self.config.get("harrix_notes_explorer_publisher")
        publisher = str(publisher_raw or "").strip()
        if not publisher:
            publisher = str(self.config.get("github_user") or "Harrix").strip().lower() or "harrix"

        source = (project_root / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not source.is_dir():
            self.add_line(f"❌ HSK extension folder not found: {source}")
            if not noninteractive:
                self.show_result()
            return

        if not noninteractive and not yes:
            confirmed = self.get_yes_no_question(
                self.title,
                f"Delete everything in\n{dest}\nexcept .git and replace with the public extension build?",
            )
            if not confirmed:
                self.add_line("Canceled.")
                self.show_result()
                return
        elif noninteractive and not yes:
            self.add_line("❌ Confirmation required for non-interactive sync.")
            self.add_line("   Pass --yes to confirm.")
            return

        self.add_line(f"Source: {source}")
        self.add_line(f"Destination: {dest}")
        self.add_line(f"Publisher: {publisher}")

        build_dir: Path | None = None
        try:
            build_dir = self._build_public_extension(source, publisher=publisher)
            for line in self._sync_to_repo(build_dir, dest, project_root=project_root):
                self.add_line(line)
        finally:
            if build_dir is not None:
                self._cleanup_build_dir(build_dir)

        self.add_line("Commit and push changes in the public repo when ready.")
        if not noninteractive:
            self.show_result()

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

    @staticmethod
    def _cleanup_build_dir(build_dir: Path) -> None:
        if build_dir.is_dir():
            shutil.rmtree(build_dir, ignore_errors=True)

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

    @staticmethod
    def _strip_cli_from_package_json(data: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
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
                contributes["commands"] = [
                    cmd for cmd in commands if not (isinstance(cmd, dict) and cmd.get("command") in command_ids)
                ]

            menus = contributes.get("menus")
            if isinstance(menus, dict):
                for menu_key, entries in list(menus.items()):
                    if not isinstance(entries, list):
                        continue
                    menus[menu_key] = [
                        entry
                        for entry in entries
                        if not (isinstance(entry, dict) and entry.get("command") in command_ids)
                    ]

        return data

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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *_args: Any, **_kwargs: Any) -> None
```

Build and sync the public extension tree into the configured repository.

<details>
<summary>Code:</summary>

```python
def execute(
        self,
        *_args: Any,
        yes: bool = False,
        noninteractive: bool = False,
        **_kwargs: Any,
    ) -> None:
        dest_raw = self.resolve_config_value(
            "path_harrix_notes_explorer",
            self.config.get("path_harrix_notes_explorer"),
        )
        dest_str = str(dest_raw or "").strip()
        if not dest_str:
            self.add_line("❌ path_harrix_notes_explorer is empty. Set it in config/config.json.")
            if not noninteractive:
                self.show_result()
            return

        dest = Path(dest_str).expanduser()
        project_root = h.dev.get_project_root().resolve()
        if dest.resolve() == project_root:
            self.add_line(f"❌ Refusing to sync into harrix-swiss-knife project root: {dest}")
            if not noninteractive:
                self.show_result()
            return

        publisher_raw = self.config.get("harrix_notes_explorer_publisher")
        publisher = str(publisher_raw or "").strip()
        if not publisher:
            publisher = str(self.config.get("github_user") or "Harrix").strip().lower() or "harrix"

        source = (project_root / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not source.is_dir():
            self.add_line(f"❌ HSK extension folder not found: {source}")
            if not noninteractive:
                self.show_result()
            return

        if not noninteractive and not yes:
            confirmed = self.get_yes_no_question(
                self.title,
                f"Delete everything in\n{dest}\nexcept .git and replace with the public extension build?",
            )
            if not confirmed:
                self.add_line("Canceled.")
                self.show_result()
                return
        elif noninteractive and not yes:
            self.add_line("❌ Confirmation required for non-interactive sync.")
            self.add_line("   Pass --yes to confirm.")
            return

        self.add_line(f"Source: {source}")
        self.add_line(f"Destination: {dest}")
        self.add_line(f"Publisher: {publisher}")

        build_dir: Path | None = None
        try:
            build_dir = self._build_public_extension(source, publisher=publisher)
            for line in self._sync_to_repo(build_dir, dest, project_root=project_root):
                self.add_line(line)
        finally:
            if build_dir is not None:
                self._cleanup_build_dir(build_dir)

        self.add_line("Commit and push changes in the public repo when ready.")
        if not noninteractive:
            self.show_result()
```

</details>

### ⚙️ Method `_apply_hsk_to_public_renames`

```python
def _apply_hsk_to_public_renames(cls, text: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _apply_hsk_to_public_renames(cls, text: str, *, publisher: str) -> str:
        for old, new in cls._HSK_TO_PUBLIC_REPLACEMENTS:
            text = text.replace(old, new)
        return re.sub(r'"publisher"\s*:\s*"local"', f'"publisher": "{publisher}"', text)
```

</details>

### ⚙️ Method `_build_public_extension`

```python
def _build_public_extension(cls, source_dir: Path) -> Path
```

Copy _source_dir_ to a temp folder, transform to public build, return temp path.

<details>
<summary>Code:</summary>

```python
def _build_public_extension(cls, source_dir: Path, *, publisher: str) -> Path:
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
```

</details>

### ⚙️ Method `_cleanup_build_dir`

```python
def _cleanup_build_dir(build_dir: Path) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _cleanup_build_dir(build_dir: Path) -> None:
        if build_dir.is_dir():
            shutil.rmtree(build_dir, ignore_errors=True)
```

</details>

### ⚙️ Method `_patch_extension_js`

```python
def _patch_extension_js(cls, content: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
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
```

</details>

### ⚙️ Method `_public_description`

```python
def _public_description(description: str) -> str
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
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
```

</details>

### ⚙️ Method `_strip_cli_from_package_json`

```python
def _strip_cli_from_package_json(data: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _strip_cli_from_package_json(data: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
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
                contributes["commands"] = [
                    cmd for cmd in commands if not (isinstance(cmd, dict) and cmd.get("command") in command_ids)
                ]

            menus = contributes.get("menus")
            if isinstance(menus, dict):
                for menu_key, entries in list(menus.items()):
                    if not isinstance(entries, list):
                        continue
                    menus[menu_key] = [
                        entry
                        for entry in entries
                        if not (isinstance(entry, dict) and entry.get("command") in command_ids)
                    ]

        return data
```

</details>

### ⚙️ Method `_sync_to_repo`

```python
def _sync_to_repo(cls, build_dir: Path, repo_root: Path) -> list[str]
```

Replace _repo_root_ contents (except `.git`) with _build_dir_; return log lines.

<details>
<summary>Code:</summary>

```python
def _sync_to_repo(cls, build_dir: Path, repo_root: Path, *, project_root: Path | None = None) -> list[str]:
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
```

</details>
