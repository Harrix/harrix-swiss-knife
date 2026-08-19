---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `repos.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_repos`](#-function-ensure_repos)
- [🔧 Function `expand_repo_snapshot`](#-function-expand_repo_snapshot)
- [🔧 Function `repo_ready_or_reset`](#-function-repo_ready_or_reset)
- [🔧 Function `update_git_repo`](#-function-update_git_repo)

</details>

## 🔧 Function `ensure_repos`

```python
def ensure_repos(install_root: Path, *, deps: Path, offline: bool, log: OutcomeLog) -> Path
```

Ensure sibling repos exist under [`install_root`](wizard.g.md#%EF%B8%8F-method-install_root). Return harrix-swiss-knife path.

<details>
<summary>Code:</summary>

```python
def ensure_repos(
    install_root: Path,
    *,
    deps: Path,
    offline: bool,
    log: OutcomeLog,
) -> Path:
    log.step("Get source repositories")
    if offline:
        log.detail("Offline EXE: extract snapshots from the bundled repos/ zip files when present")
    else:
        log.detail("Online EXE: git clone from GitHub (or git pull if the folder already exists)")
    hsk_path = install_root / "harrix-swiss-knife"
    for name in REPO_NAMES:
        path = install_root / name
        if repo_ready_or_reset(path, label=name, allow_offline=offline, log=log):
            log.detail(f"{name} already present at {path}")
            log.add("already", f"{name} already present")
            if not offline:
                log.detail(f"Updating {name} with git pull --ff-only (skipped if there are local changes)")
                update_git_repo(path, label=name, log=log)
            continue
        snap = deps / "repos" / f"{name}.zip"
        if offline and snap.is_file():
            log.detail(f"Extracting {name} from bundled snapshot {snap.name}")
            expand_repo_snapshot(snap, path)
            log.add("installed", f"Extracted {name} from offline snapshot")
            continue
        url = _REPO_URLS[name]
        log.detail(f"git clone {url}")
        code = _git(["-C", str(install_root), "clone", url], log)
        if code != 0:
            msg = f"git clone {name} failed (exit {code})"
            raise RuntimeError(msg)
        log.add("installed", f"Cloned {name} from GitHub")
    return hsk_path
```

</details>

## 🔧 Function `expand_repo_snapshot`

```python
def expand_repo_snapshot(zip_path: Path, destination: Path) -> None
```

Extract a repository snapshot zip into `destination`.

<details>
<summary>Code:</summary>

```python
def expand_repo_snapshot(zip_path: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(destination)
```

</details>

## 🔧 Function `repo_ready_or_reset`

```python
def repo_ready_or_reset(path: Path, *, label: str, allow_offline: bool, log: OutcomeLog) -> bool
```

Return whether `path` is a usable repo; reset empty non-git folders.

<details>
<summary>Code:</summary>

```python
def repo_ready_or_reset(path: Path, *, label: str, allow_offline: bool, log: OutcomeLog) -> bool:
    if not path.exists():
        return False
    if (path / ".git").exists():
        return True
    items = list(path.iterdir()) if path.is_dir() else []
    if not items:
        log.detail(f"Removing empty non-git folder: {path}")
        path.rmdir()
        return False
    if allow_offline and (path / "pyproject.toml").is_file():
        log.detail(f"{label} present as offline snapshot (no .git); skip re-extract")
        return True
    msg = f"{label} folder exists but is not a git repository: {path}"
    raise RuntimeError(msg)
```

</details>

## 🔧 Function `update_git_repo`

```python
def update_git_repo(path: Path, *, label: str, log: OutcomeLog) -> None
```

Fast-forward `path` when it is a clean Git checkout.

<details>
<summary>Code:</summary>

```python
def update_git_repo(path: Path, *, label: str, log: OutcomeLog) -> None:
    git_exe = shutil.which("git")
    if git_exe is None:
        log.add("skipped", f"{label} not updated (git not available)")
        return
    if not (path / ".git").is_dir():
        log.add("skipped", f"{label} not updated (no .git folder)")
        return
    status = subprocess.run(
        [git_exe, "-C", str(path), "status", "--porcelain"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    if status.returncode != 0:
        log.add("skipped", f"{label} not updated (git status failed)")
        return
    if status.stdout.strip():
        log.add("skipped", f"{label} not updated (local changes present)")
        return
    if _git(["-C", str(path), "fetch", "--prune"], log) != 0:
        log.add("skipped", f"{label} not updated (git fetch failed)")
        return
    if _git(["-C", str(path), "pull", "--ff-only"], log) != 0:
        log.add("skipped", f"{label} not updated (git pull failed)")
        return
    log.add("installed", f"Updated {label} (git pull)")
```

</details>
