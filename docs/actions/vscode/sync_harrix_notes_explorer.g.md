---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `sync_harrix_notes_explorer.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSyncHarrixNotesExplorer`](#%EF%B8%8F-class-onsyncharrixnotesexplorer)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `resolve_public_publisher`](#%EF%B8%8F-method-resolve_public_publisher)
  - [⚙️ Method `resolve_public_repo_path`](#%EF%B8%8F-method-resolve_public_repo_path)
  - [⚙️ Method `sync_public_repo`](#%EF%B8%8F-method-sync_public_repo)

</details>

## 🏛️ Class `OnSyncHarrixNotesExplorer`

```python
class OnSyncHarrixNotesExplorer(ActionBase)
```

Build public extension from `vscode/harrix-notes-explorer-hsk` into `path_harrix_notes_explorer`.

Strips HSK/CLI bits, renames identifiers for the public package, and replaces the public
repo contents while keeping `.git/`.

<details>
<summary>Code:</summary>

```python
class OnSyncHarrixNotesExplorer(ActionBase):

    icon = "🔄"
    title = "Sync Harrix Notes Explorer public repo"
    cli_available = True
    cli_hint = "vscode sync-notes-explorer"

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
    def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        """Sync HSK extension sources into the public notes-explorer repo."""
        ok = self.sync_public_repo()
        if not noninteractive:
            if not self.result_lines and not ok:
                self.add_line("Canceled or sync failed.")
            self.show_result()

    def resolve_public_publisher(self) -> str:
        """Return publisher ID from config (`harrix_notes_explorer_publisher` or `github_user`)."""
        publisher_raw = self.config.get("harrix_notes_explorer_publisher")
        publisher = str(publisher_raw or "").strip()
        if not publisher:
            publisher = str(self.config.get("github_user") or "Harrix").strip().lower() or "harrix"
        return publisher

    def resolve_public_repo_path(self) -> Path | None:
        """Return configured public repo path, or `None` when unset."""
        dest_raw = self.resolve_config_value(
            "path_harrix_notes_explorer",
            self.config.get("path_harrix_notes_explorer"),
        )
        dest_str = str(dest_raw or "").strip()
        if not dest_str:
            return None
        return Path(dest_str).expanduser()

    def sync_public_repo(self) -> bool:
        """Build public extension and sync into configured repo.

        Returns:

        - `bool`: `True` on success or when the public path is unset (skipped with a warning);
          `False` on a fatal error.

        """
        project_root = h.dev.get_project_root().resolve()
        hsk_dir = (project_root / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not hsk_dir.is_dir():
            self.add_line(f"❌ HSK extension folder not found: {hsk_dir}")
            return False

        public_repo = self.resolve_public_repo_path()
        if public_repo is None:
            self.add_line(
                "⚠️ path_harrix_notes_explorer is empty; skipped public repo sync. "
                "Set it in config/config.json to publish the public build."
            )
            return True

        publisher = self.resolve_public_publisher()
        return self._sync_public_repo(public_repo, hsk_dir, project_root, publisher)

    @classmethod
    def _apply_hsk_to_public_renames(cls, text: str, *, publisher: str) -> str:
        for old, new in cls._HSK_TO_PUBLIC_REPLACEMENTS:
            text = text.replace(old, new)
        return re.sub(r'"publisher"\s*:\s*"local"', f'"publisher": "{publisher}"', text)

    @classmethod
    def _build_public_extension(cls, source_dir: Path, *, publisher: str) -> Path:
        """Copy `source_dir` to a temp folder, transform to public build, return temp path."""
        source_dir = source_dir.resolve()
        if not source_dir.is_dir():
            msg = f"Extension source not found: {source_dir}"
            raise FileNotFoundError(msg)

        build_dir = Path(tempfile.mkdtemp(prefix="harrix-notes-explorer-public-"))
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", ".biome")
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
            elif path.name == "icons-browse-menu.js":
                text = cls._strip_cli_from_icons_browse_menu(text, manifest)
                text = cls._apply_hsk_to_public_renames(text, publisher=publisher)
            else:
                text = cls._apply_hsk_to_public_renames(text, publisher=publisher)
            path.write_text(text, encoding="utf-8", newline="\n")

        return build_dir

    @staticmethod
    def _cleanup_build_dir(build_dir: Path) -> None:
        if build_dir.is_dir():
            shutil.rmtree(build_dir, ignore_errors=True)

    @staticmethod
    def _cli_command_short_names(manifest: dict[str, Any]) -> list[str]:
        """Return command suffixes from `package.harrix-cli.contributes.json` (`beautifyMd`, …)."""
        raw = manifest.get("commandIds")
        if not isinstance(raw, list):
            return []
        names: list[str] = []
        for command_id in raw:
            if not isinstance(command_id, str) or "." not in command_id:
                continue
            short = command_id.rsplit(".", 1)[-1]
            if short:
                names.append(short)
        return names

    @staticmethod
    def _item_command_in_set(item: object, command_ids: set[str]) -> bool:
        if not isinstance(item, dict):
            return False
        command = cast("dict[str, Any]", item).get("command")
        return isinstance(command, str) and command in command_ids

    @classmethod
    def _patch_extension_js(cls, content: str) -> str:
        content = re.sub(
            r"/\*\* hsk integration.*?\*/\s*",
            "",
            content,
            count=1,
            flags=re.DOTALL,
        )
        content = re.sub(r"const harrixCli = require\('\./harrix-cli'\);\s*\n", "", content)

        content = re.sub(
            r"\s*\|\|\s*harrixCli\.folderListedWithoutMarkdown\(\s*e\.name,\s*"
            r"(?:this\.getTemplatesForFolder\(path\.join\(dir, e\.name\)\)\.length|"
            r"templateCountFor\(path\.join\(dir, e\.name\)\))\s*\)",
            "",
            content,
        )

        content = re.sub(
            r"\s*\|\|\s*harrixCli\.isSpecialNotesFolderName\(e\.name\)",
            "",
            content,
        )

        # Icons Browse / shared listing: after CLI strip, template counts are always 0.
        content = re.sub(
            r"templateCountFor:\s*\(folderPath\)\s*=>\s*this\.getTemplatesForFolder\(folderPath\)\.length,",
            "templateCountFor: () => 0,",
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
        desc = re.sub(r"\s*with hsk integration\s*", "", desc, flags=re.IGNORECASE)
        desc = desc.strip(" —")
        if not desc or desc == "Harrix Notes Explorer":
            return "Harrix Notes Explorer — custom notes panel for markdown notes"
        if "with hsk integration" in desc.lower():
            return "Harrix Notes Explorer — custom notes panel for markdown notes"
        return desc

    @classmethod
    def _strip_cli_from_icons_browse_menu(cls, content: str, manifest: dict[str, Any]) -> str:
        """Remove HSK CLI command IDs and menu items from Icons Browse context menu."""
        short_names = cls._cli_command_short_names(manifest)
        for short_name in short_names:
            content = re.sub(
                rf"^[ \t]*{re.escape(short_name)}:[ \t]*'harrixNotesExplorerHsk\.{re.escape(short_name)}',[ \t]*\n",
                "",
                content,
                flags=re.MULTILINE,
            )
            content = re.sub(
                rf"^[ \t]*out\.push\(item\(CMD\.{re.escape(short_name)},[^;\n]*\);[ \t]*\n",
                "",
                content,
                flags=re.MULTILINE,
            )

        content = re.sub(r"\n[ \t]*if \(base\.includes\('[^']+'\)\) \{\s*\}", "", content)
        content = re.sub(
            r"const pushFolderCli = \(\) => \{\s*out\.push\(sep\(\)\);\s*"
            r"if \(isGit\) \{\n"
            r"      out\.push\(item\(CMD\.discardGitChangesInFolder, ([^)]+)\)\);\n"
            r"    \}\n"
            r"  \};",
            "const pushFolderCli = () => {\n"
            "    if (isGit) {\n"
            "      out.push(sep());\n"
            "      out.push(item(CMD.discardGitChangesInFolder, \\1));\n"
            "    }\n"
            "  };",
            content,
        )
        content = re.sub(
            r"const pushFolderCli = \(\) => \{\s*out\.push\(sep\(\)\);\s*\};",
            "const pushFolderCli = () => {};",
            content,
        )

        leftover = [
            name
            for name in short_names
            if re.search(rf"\bCMD\.{re.escape(name)}\b", content)
            or re.search(rf"harrixNotesExplorerHsk\.{re.escape(name)}\b", content)
        ]
        if leftover:
            msg = "icons-browse-menu.js still references CLI commands after public build patch: " + ", ".join(leftover)
            raise ValueError(msg)
        return content

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
        """Build public extension and sync into `dest`; return `False` on fatal error."""
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
        """Replace `repo_root` contents (except `.git`) with `build_dir`; return log lines."""
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
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None
```

Sync HSK extension sources into the public notes-explorer repo.

<details>
<summary>Code:</summary>

```python
def execute(self, *_args: Any, noninteractive: bool = False, **_kwargs: Any) -> None:
        ok = self.sync_public_repo()
        if not noninteractive:
            if not self.result_lines and not ok:
                self.add_line("Canceled or sync failed.")
            self.show_result()
```

</details>

### ⚙️ Method `resolve_public_publisher`

```python
def resolve_public_publisher(self) -> str
```

Return publisher ID from config (`harrix_notes_explorer_publisher` or `github_user`).

<details>
<summary>Code:</summary>

```python
def resolve_public_publisher(self) -> str:
        publisher_raw = self.config.get("harrix_notes_explorer_publisher")
        publisher = str(publisher_raw or "").strip()
        if not publisher:
            publisher = str(self.config.get("github_user") or "Harrix").strip().lower() or "harrix"
        return publisher
```

</details>

### ⚙️ Method `resolve_public_repo_path`

```python
def resolve_public_repo_path(self) -> Path | None
```

Return configured public repo path, or `None` when unset.

<details>
<summary>Code:</summary>

```python
def resolve_public_repo_path(self) -> Path | None:
        dest_raw = self.resolve_config_value(
            "path_harrix_notes_explorer",
            self.config.get("path_harrix_notes_explorer"),
        )
        dest_str = str(dest_raw or "").strip()
        if not dest_str:
            return None
        return Path(dest_str).expanduser()
```

</details>

### ⚙️ Method `sync_public_repo`

```python
def sync_public_repo(self) -> bool
```

Build public extension and sync into configured repo.

Returns:

- `bool`: `True` on success or when the public path is unset (skipped with a warning);
  `False` on a fatal error.

<details>
<summary>Code:</summary>

```python
def sync_public_repo(self) -> bool:
        project_root = h.dev.get_project_root().resolve()
        hsk_dir = (project_root / "vscode" / "harrix-notes-explorer-hsk").resolve()
        if not hsk_dir.is_dir():
            self.add_line(f"❌ HSK extension folder not found: {hsk_dir}")
            return False

        public_repo = self.resolve_public_repo_path()
        if public_repo is None:
            self.add_line(
                "⚠️ path_harrix_notes_explorer is empty; skipped public repo sync. "
                "Set it in config/config.json to publish the public build."
            )
            return True

        publisher = self.resolve_public_publisher()
        return self._sync_public_repo(public_repo, hsk_dir, project_root, publisher)
```

</details>
