---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `setup_data_for_hsk.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnSetupDataForHsk`](#%EF%B8%8F-class-onsetupdataforhsk)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
- [🔧 Function `run_setup_data_for_hsk_dialog`](#-function-run_setup_data_for_hsk_dialog)

</details>

## 🏛️ Class `OnSetupDataForHsk`

```python
class OnSetupDataForHsk(ActionBase)
```

Create `data-for-hsk` with databases, Notes folders, and Git repos.

<details>
<summary>Code:</summary>

```python
class OnSetupDataForHsk(ActionBase):

    icon = "📁"
    title = "Set up data-for-hsk"
    cli_available = True
    cli_hint = "dev setup-data-for-hsk"

    @ActionBase.handle_exceptions("set up data-for-hsk")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Pick a parent folder, create `data-for-hsk`, and wire config paths."""
        noninteractive = bool(kwargs.get("noninteractive"))
        parent_dir = kwargs.get("parent_dir")
        if noninteractive and not parent_dir:
            self.add_line("❌ CLI requires `--parent` for non-interactive setup.")
            return
        if parent_dir:
            data_root = Path(str(parent_dir)).expanduser() / _DATA_FOR_HSK_DIR_NAME
            notes_folders = read_notes_folder_names(self.config)
            try:
                result = apply_data_for_hsk_to_config(data_root, notes_folders)
            except OSError as exc:
                self.add_line(f"❌ Failed to create data-for-hsk: {exc}")
                return
            self.add_line(f"✅ data-for-hsk ready at `{result.data_root}`")
            return
        run_setup_data_for_hsk_dialog(self.config, parent=None, log=logger, action=self)
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Pick a parent folder, create `data-for-hsk`, and wire config paths.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        noninteractive = bool(kwargs.get("noninteractive"))
        parent_dir = kwargs.get("parent_dir")
        if noninteractive and not parent_dir:
            self.add_line("❌ CLI requires `--parent` for non-interactive setup.")
            return
        if parent_dir:
            data_root = Path(str(parent_dir)).expanduser() / _DATA_FOR_HSK_DIR_NAME
            notes_folders = read_notes_folder_names(self.config)
            try:
                result = apply_data_for_hsk_to_config(data_root, notes_folders)
            except OSError as exc:
                self.add_line(f"❌ Failed to create data-for-hsk: {exc}")
                return
            self.add_line(f"✅ data-for-hsk ready at `{result.data_root}`")
            return
        run_setup_data_for_hsk_dialog(self.config, parent=None, log=logger, action=self)
```

</details>

## 🔧 Function `run_setup_data_for_hsk_dialog`

```python
def run_setup_data_for_hsk_dialog(config: dict[str, Any], *, parent: Any = None, log: logging.Logger | None = None, action: ActionBase | None = None) -> bool
```

Ask for a parent directory and run `data-for-hsk` setup. Returns success.

<details>
<summary>Code:</summary>

```python
def run_setup_data_for_hsk_dialog(
    config: dict[str, Any],
    *,
    parent: Any = None,
    log: logging.Logger | None = None,
    action: ActionBase | None = None,
) -> bool:
    log = log or logger
    default_parent = suggest_data_for_hsk_root(config).parent
    if action is not None:
        parent_dir = action.get_existing_directory(
            "Select folder for data-for-hsk",
            str(default_parent),
        )
    else:
        selected = QFileDialog.getExistingDirectory(parent, "Select folder for data-for-hsk", str(default_parent))
        parent_dir = Path(selected) if selected else None

    if parent_dir is None:
        if action is not None:
            action.add_line("Cancelled.")
        return False

    data_root = parent_dir / _DATA_FOR_HSK_DIR_NAME
    notes_folders = read_notes_folder_names(config)

    if data_root.is_dir() and any(data_root.iterdir()):
        message = (
            f"`{data_root}` already exists and is not empty.\n\n"
            "Missing databases and folders will be added; existing files are kept."
        )
        if action is not None:
            if not action.get_yes_no_question("Folder exists", message, default_yes=True):
                action.add_line("Cancelled.")
                return False
        else:
            reply = QMessageBox.question(
                parent,
                "Folder exists",
                message,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False

    try:
        result = apply_data_for_hsk_to_config(data_root, notes_folders)
    except OSError:
        text = "Failed to create data-for-hsk"
        log.exception(text)
        if action is not None:
            action.add_line(f"❌ {text}")
        return False

    lines = [
        f"✅ data-for-hsk ready at `{result.data_root}`",
        f"Databases: `{result.databases_dir}`",
        f"Notes: `{result.notes_dir}`",
    ]
    if result.created_databases:
        lines.append(f"Created databases: {', '.join(result.created_databases)}")
    if result.git_repos_created:
        lines.append(f"Git repositories: {len(result.git_repos_created)}")
    lines.append("Restart Harrix Swiss Knife or reopen apps so config changes apply.")

    for line in lines:
        log.info(line)
        if action is not None:
            action.add_line(line)

    return True
```

</details>
