---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `paths.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `default_install_root_parent`](#-function-default_install_root_parent)
- [🔧 Function `detect_dev_checkout_parent`](#-function-detect_dev_checkout_parent)
- [🔧 Function `normalize_install_root`](#-function-normalize_install_root)

</details>

## 🔧 Function `default_install_root_parent`

```python
def default_install_root_parent() -> Path
```

Prefer `D:\GitHub`, `C:\GitHub`, Documents\GitHub, else `%USERPROFILE%\harrix-swiss-knife`.

<details>
<summary>Code:</summary>

```python
def default_install_root_parent() -> Path:
    docs = Path.home() / "Documents" / "GitHub"
    for candidate in (Path(r"D:\GitHub"), Path(r"C:\GitHub"), docs):
        if candidate.is_dir():
            return candidate.resolve()
    bundle = Path.home() / "harrix-swiss-knife"
    bundle.mkdir(parents=True, exist_ok=True)
    return bundle.resolve()
```

</details>

## 🔧 Function `detect_dev_checkout_parent`

```python
def detect_dev_checkout_parent(project_hint: Path | None = None) -> Path | None
```

If running from a harrix-swiss-knife checkout, return its parent folder.

<details>
<summary>Code:</summary>

```python
def detect_dev_checkout_parent(project_hint: Path | None = None) -> Path | None:
    candidates: list[Path] = []
    if project_hint is not None:
        candidates.append(project_hint)
    # installer package -> harrix_swiss_knife -> src -> repo root
    here = Path(__file__).resolve()
    candidates.append(here.parents[3] if len(here.parents) >= _REPO_ROOT_PARENT_DEPTH else here.parent)
    for root in candidates:
        pp = root / "pyproject.toml"
        if not pp.is_file():
            continue
        text = pp.read_text(encoding="utf-8", errors="replace")[:2000]
        if 'name = "harrix-swiss-knife"' in text or "name='harrix-swiss-knife'" in text:
            return root.parent.resolve()
    return None
```

</details>

## 🔧 Function `normalize_install_root`

```python
def normalize_install_root(selected: Path) -> Path
```

Accept …\GitHub or …\harrix-swiss-knife; otherwise append GitHub.

<details>
<summary>Code:</summary>

```python
def normalize_install_root(selected: Path) -> Path:
    p = selected.resolve()
    leaf = p.name
    program_files = (
        os.environ.get("PROGRAMFILES") or os.environ.get("ProgramFiles") or r"C:\Program Files"  # noqa: SIM112
    )
    under_pf = str(p).lower().startswith(program_files.lower())
    under_user = str(p).lower().startswith(str(Path.home()).lower())
    if leaf.lower() == "github" or (leaf.lower() == "harrix-swiss-knife" and (under_pf or under_user)):
        p.mkdir(parents=True, exist_ok=True)
        return p
    gh = p / "GitHub"
    gh.mkdir(parents=True, exist_ok=True)
    return gh.resolve()
```

</details>
