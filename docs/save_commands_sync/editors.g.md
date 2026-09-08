---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `editors.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `canonical_editor_label`](#-function-canonical_editor_label)
- [🔧 Function `discover_editors`](#-function-discover_editors)
- [🔧 Function `editor_choice_label`](#-function-editor_choice_label)
- [🔧 Function `extensions_root`](#-function-extensions_root)
- [🔧 Function `resolve_editor_cli_token`](#-function-resolve_editor_cli_token)
- [🔧 Function `roaming_app_data`](#-function-roaming_app_data)
- [🔧 Function `running_editor_names`](#-function-running_editor_names)
- [🔧 Function `save_commands_extension_installed`](#-function-save_commands_extension_installed)
- [🔧 Function `state_vscdb_path`](#-function-state_vscdb_path)

</details>

## 🔧 Function `canonical_editor_label`

```python
def canonical_editor_label(display: str) -> str
```

Strip `(not installed)` from a checkbox label.

<details>
<summary>Code:</summary>

```python
def canonical_editor_label(display: str) -> str:
    return _Install._canonical_editor_label(display)  # noqa: SLF001
```

</details>

## 🔧 Function `discover_editors`

```python
def discover_editors() -> list[str]
```

Return labels for editors that look installed or already have user data.

<details>
<summary>Code:</summary>

```python
def discover_editors() -> list[str]:
    if sys.platform == "win32":
        found = list(_Install._discover_win32_editors())  # noqa: SLF001
        extra = [label for label in SUPPORTED_EDITOR_LABELS if label not in found and _editor_has_user_data(label)]
        return found + extra
    return [label for label in SUPPORTED_EDITOR_LABELS if _editor_has_user_data(label)]
```

</details>

## 🔧 Function `editor_choice_label`

```python
def editor_choice_label(canonical: str, *, installed: bool) -> str
```

Return dialog checkbox text for `canonical` editor name.

<details>
<summary>Code:</summary>

```python
def editor_choice_label(canonical: str, *, installed: bool) -> str:
    return _Install._editor_choice_label(canonical, installed=installed)  # noqa: SLF001
```

</details>

## 🔧 Function `extensions_root`

```python
def extensions_root(label: str) -> Path | None
```

Return the user `extensions` directory for `label`, or `None` if unknown.

<details>
<summary>Code:</summary>

```python
def extensions_root(label: str) -> Path | None:
    pairs = _Install._dest_extension_roots([label])  # noqa: SLF001
    if not pairs:
        return None
    return pairs[0][1]
```

</details>

## 🔧 Function `resolve_editor_cli_token`

```python
def resolve_editor_cli_token(token: str) -> str | None
```

Map a CLI editor token (and aliases) to a canonical display label.

<details>
<summary>Code:</summary>

```python
def resolve_editor_cli_token(token: str) -> str | None:
    return _Install._resolve_editor_cli_token(token)  # noqa: SLF001
```

</details>

## 🔧 Function `roaming_app_data`

```python
def roaming_app_data() -> Path
```

Return the OS roaming/config directory that holds VS Code-family user data.

<details>
<summary>Code:</summary>

```python
def roaming_app_data() -> Path:
    if sys.platform == "win32":
        roaming = os.environ.get("APPDATA")
        if roaming:
            return Path(roaming)
        return Path.home() / "AppData" / "Roaming"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support"
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return Path(xdg) if xdg else Path.home() / ".config"
```

</details>

## 🔧 Function `running_editor_names`

```python
def running_editor_names(labels: Iterable[str]) -> list[str]
```

Return display names of selected editors whose process is running (Windows).

<details>
<summary>Code:</summary>

```python
def running_editor_names(labels: Iterable[str]) -> list[str]:
    names: list[str] = []
    for label in labels:
        image = _PROCESS_IMAGE_NAMES.get(label)
        if image and is_process_running(image):
            names.append(label)
    return names
```

</details>

## 🔧 Function `save_commands_extension_installed`

```python
def save_commands_extension_installed(label: str) -> bool
```

Return whether the Save Commands extension folder exists for `label`.

<details>
<summary>Code:</summary>

```python
def save_commands_extension_installed(label: str) -> bool:
    root = extensions_root(label)
    if root is None or not root.is_dir():
        return False
    try:
        children = root.iterdir()
    except OSError:
        return False
    prefix = EXTENSION_FOLDER_PREFIX.casefold()
    return any(path.is_dir() and path.name.casefold().startswith(prefix) for path in children)
```

</details>

## 🔧 Function `state_vscdb_path`

```python
def state_vscdb_path(label: str) -> Path | None
```

Return `User/globalStorage/state.vscdb` for `label`, or `None` if unknown.

<details>
<summary>Code:</summary>

```python
def state_vscdb_path(label: str) -> Path | None:
    folder = _USER_DATA_DIR_NAMES.get(label)
    if folder is None:
        return None
    return roaming_app_data() / folder / "User" / "globalStorage" / "state.vscdb"
```

</details>
