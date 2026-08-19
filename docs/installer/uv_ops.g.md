---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `uv_ops.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `ensure_uv_tool_bin_on_path`](#-function-ensure_uv_tool_bin_on_path)
- [🔧 Function `install_hsk_cli`](#-function-install_hsk_cli)
- [🔧 Function `uv_sync_with_bundle_cache`](#-function-uv_sync_with_bundle_cache)

</details>

## 🔧 Function `ensure_uv_tool_bin_on_path`

```python
def ensure_uv_tool_bin_on_path(log: OutcomeLog) -> None
```

Prepend `~/.local/bin` to the user PATH when uv tools are installed there.

<details>
<summary>Code:</summary>

```python
def ensure_uv_tool_bin_on_path(log: OutcomeLog) -> None:
    bin_dir = Path.home() / ".local" / "bin"
    if not bin_dir.is_dir():
        return
    if winreg is None:
        refresh_path()
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
            try:
                user_path, _ = winreg.QueryValueEx(key, "Path")
            except OSError:
                user_path = ""
            bin_s = str(bin_dir)
            parts = [p for p in str(user_path).split(";") if p]
            if any(p.lower() == bin_s.lower() for p in parts):
                return
            new_path = bin_s if not parts else f"{bin_s};{user_path}"
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            log.detail(f"Added {bin_dir} to user PATH")
    except OSError:
        pass
    refresh_path()
```

</details>

## 🔧 Function `install_hsk_cli`

```python
def install_hsk_cli(hsk_path: Path, log: OutcomeLog) -> None
```

Install the editable `hsk` CLI globally via `uv tool install -e`.

<details>
<summary>Code:</summary>

```python
def install_hsk_cli(hsk_path: Path, log: OutcomeLog) -> None:
    log.step("uv tool install -e (global hsk CLI on PATH)")
    uv = find_uv_exe()
    if uv is None:
        log.add("skipped", "CLI not installed (uv missing)")
        return
    if not (hsk_path / "pyproject.toml").is_file():
        log.add("skipped", "CLI not installed (pyproject.toml missing)")
        return
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    listed = subprocess.run(
        [str(uv), "tool", "list"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creation,
    )
    tool_text = listed.stdout or ""
    args = ["tool", "install", "--reinstall", "-e", str(hsk_path)]
    if "harrix-swiss-knife" not in tool_text:
        args = ["tool", "install", "-e", str(hsk_path)]
    proc = subprocess.run(
        [str(uv), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creation,
    )
    if proc.stdout.strip():
        log.detail(proc.stdout.strip()[:2000])
    if proc.stderr.strip():
        log.detail(proc.stderr.strip()[:2000])
    if proc.returncode != 0:
        log.add("skipped", "CLI not installed (uv tool install failed; run Dev -> Install CLI)")
        return
    ensure_uv_tool_bin_on_path(log)
    log.add("installed", "Installed global CLI (hsk on PATH via uv tool install -e)")
```

</details>

## 🔧 Function `uv_sync_with_bundle_cache`

```python
def uv_sync_with_bundle_cache(repo_path: Path, *, deps: Path, label: str, log: OutcomeLog) -> bool
```

Run `uv sync`, preferring offline cache. Return whether offline cache was used.

<details>
<summary>Code:</summary>

```python
def uv_sync_with_bundle_cache(repo_path: Path, *, deps: Path, label: str, log: OutcomeLog) -> bool:
    uv = find_uv_exe()
    if uv is None:
        msg = "uv was not found"
        raise RuntimeError(msg)
    cache = deps / "uv-cache"
    python_cache = deps / "uv-python-cache"
    env = os.environ.copy()
    used_offline = False
    if cache.is_dir():
        env["UV_CACHE_DIR"] = str(cache)
        log.detail(f"Using offline uv cache: {cache}")
    if python_cache.is_dir():
        env["UV_PYTHON_CACHE_DIR"] = str(python_cache)
        log.detail(f"Using offline uv python cache: {python_cache}")
    creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    def _run(args: list[str]) -> int:
        proc = subprocess.run(
            [str(uv), *args],
            cwd=str(repo_path),
            env=env,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=creation,
        )
        for stream in (proc.stdout, proc.stderr):
            if stream and stream.strip():
                log.detail(stream.strip()[:3000])
        return int(proc.returncode)

    if cache.is_dir():
        code = _run(["sync", "--offline"])
        if code == 0:
            used_offline = True
        else:
            log.detail(f"uv sync --offline failed for {label}; retrying online…")
            code = _run(["sync"])
    else:
        code = _run(["sync"])
    if code != 0:
        msg = f"uv sync failed in {label} (exit {code})"
        raise RuntimeError(msg)
    return used_offline
```

</details>
