---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `vscode_extension_path.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [📎 Constant `EXTENSION_RELATIVE`](#-constant-extension_relative)
- [🔧 Function `ensure_node_modules`](#-function-ensure_node_modules)
- [🔧 Function `resolve_extension_dir`](#-function-resolve_extension_dir)
- [🔧 Function `resolve_npm`](#-function-resolve_npm)
- [🔧 Function `run_npm`](#-function-run_npm)

</details>

## 📎 Constant `EXTENSION_RELATIVE`

```python
EXTENSION_RELATIVE = Path('vscode') / 'harrix-notes-explorer-hsk'
```

_No docstring provided._

## 🔧 Function `ensure_node_modules`

```python
def ensure_node_modules(extension_dir: Path) -> subprocess.CompletedProcess[str] | None
```

Run `npm ci` or `npm install` when `node_modules` is missing.

Returns the completed process if install was run, or `None` if dependencies
were already present.

<details>
<summary>Code:</summary>

```python
def ensure_node_modules(extension_dir: Path) -> subprocess.CompletedProcess[str] | None:
    if (extension_dir / "node_modules" / "@biomejs" / "biome").is_dir():
        return None

    if resolve_npm() is None:
        msg = "npm not found"
        raise FileNotFoundError(msg)

    lockfile = extension_dir / "package-lock.json"
    return run_npm(extension_dir, "ci" if lockfile.is_file() else "install")
```

</details>

## 🔧 Function `resolve_extension_dir`

```python
def resolve_extension_dir() -> Path | None
```

Return the Notes Explorer extension folder if ``package.json`` exists.

<details>
<summary>Code:</summary>

```python
def resolve_extension_dir() -> Path | None:
    extension_dir = h.dev.get_project_root() / EXTENSION_RELATIVE
    if not extension_dir.is_dir():
        return None
    if not (extension_dir / "package.json").is_file():
        return None
    return extension_dir
```

</details>

## 🔧 Function `resolve_npm`

```python
def resolve_npm() -> str | None
```

Return path to ``npm`` / ``npm.cmd`` on PATH, or ``None``.

<details>
<summary>Code:</summary>

```python
def resolve_npm() -> str | None:
    for name in ("npm.cmd", "npm"):
        found = shutil.which(name)
        if found:
            return found
    return None
```

</details>

## 🔧 Function `run_npm`

```python
def run_npm(extension_dir: Path, *npm_args: str) -> subprocess.CompletedProcess[str]
```

Run ``npm`` with the given args in the extension directory.

<details>
<summary>Code:</summary>

```python
def run_npm(extension_dir: Path, *npm_args: str) -> subprocess.CompletedProcess[str]:
    npm = resolve_npm()
    if npm is None:
        msg = "npm not found on PATH"
        raise FileNotFoundError(msg)

    return subprocess.run(
        [npm, *npm_args],
        cwd=str(extension_dir),
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        shell=False,
        timeout=600.0,
    )
```

</details>
