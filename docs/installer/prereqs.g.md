---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `prereqs.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DetectionStatus`](#%EF%B8%8F-class-detectionstatus)
- [🏛️ Class `PrerequisitePlan`](#%EF%B8%8F-class-prerequisiteplan)
  - [⚙️ Method `need_elevate (property)`](#%EF%B8%8F-method-need_elevate-property)
- [🔧 Function `any_code_editor_exists`](#-function-any_code_editor_exists)
- [🔧 Function `command_exists`](#-function-command_exists)
- [🔧 Function `default_plan_from_detection`](#-function-default_plan_from_detection)
- [🔧 Function `detect_status`](#-function-detect_status)
- [🔧 Function `ensure_managed_python`](#-function-ensure_managed_python)
- [🔧 Function `find_local_dependency`](#-function-find_local_dependency)
- [🔧 Function `find_uv_exe`](#-function-find_uv_exe)
- [🔧 Function `find_winget`](#-function-find_winget)
- [🔧 Function `install_prerequisites`](#-function-install_prerequisites)
- [🔧 Function `install_uv_from_zip`](#-function-install_uv_from_zip)
- [🔧 Function `managed_python_exists`](#-function-managed_python_exists)
- [🔧 Function `refresh_path`](#-function-refresh_path)
- [🔧 Function `run_silent_setup`](#-function-run_silent_setup)
- [🔧 Function `winget_install`](#-function-winget_install)

</details>

## 🏛️ Class `DetectionStatus`

```python
class DetectionStatus
```

Current presence of tools on the machine.

<details>
<summary>Code:</summary>

```python
class DetectionStatus:

    git: bool
    uv: bool
    editor: bool
    managed_python: bool
    git_path: str | None = None
    uv_path: str | None = None
```

</details>

## 🏛️ Class `PrerequisitePlan`

```python
class PrerequisitePlan
```

Which tools the user wants installed.

<details>
<summary>Code:</summary>

```python
class PrerequisitePlan:

    git: bool = True
    uv: bool = True
    vscode: bool = True
    python: bool = True
    python_extension: bool = True

    @property
    def need_elevate(self) -> bool:
        """Return whether Git or VS Code installation requires elevation."""
        return self.git or self.vscode
```

</details>

### ⚙️ Method `need_elevate (property)`

```python
def need_elevate(self) -> bool
```

Return whether Git or VS Code installation requires elevation.

<details>
<summary>Code:</summary>

```python
def need_elevate(self) -> bool:
        return self.git or self.vscode
```

</details>

## 🔧 Function `any_code_editor_exists`

```python
def any_code_editor_exists() -> bool
```

Return whether a supported code editor executable is installed.

<details>
<summary>Code:</summary>

```python
def any_code_editor_exists() -> bool:
    for name in ("cursor", "code", "code-insiders", "codium", "windsurf", "antigravity"):
        if command_exists(name):
            return True
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    pf = _program_files()
    pf86 = _program_files_x86()
    candidates = [
        local / "Programs" / "cursor" / "Cursor.exe",
        local / "Programs" / "Microsoft VS Code" / "Code.exe",
        local / "Programs" / "Microsoft VS Code Insiders" / "Code - Insiders.exe",
        pf / "Microsoft VS Code" / "Code.exe",
        pf86 / "Microsoft VS Code" / "Code.exe",
        local / "Programs" / "VSCodium" / "VSCodium.exe",
        pf / "VSCodium" / "VSCodium.exe",
        local / "Programs" / "Windsurf" / "Windsurf.exe",
        pf / "Windsurf" / "Windsurf.exe",
        local / "Programs" / "Antigravity" / "Antigravity.exe",
        pf / "Antigravity" / "Antigravity.exe",
    ]
    return any(p.is_file() for p in candidates)
```

</details>

## 🔧 Function `command_exists`

```python
def command_exists(name: str) -> bool
```

Return whether `name` is available on PATH.

<details>
<summary>Code:</summary>

```python
def command_exists(name: str) -> bool:
    return shutil.which(name) is not None
```

</details>

## 🔧 Function `default_plan_from_detection`

```python
def default_plan_from_detection(status: DetectionStatus) -> PrerequisitePlan
```

Build a default install plan from detected tool presence.

<details>
<summary>Code:</summary>

```python
def default_plan_from_detection(status: DetectionStatus) -> PrerequisitePlan:
    return PrerequisitePlan(
        git=not status.git,
        uv=not status.uv,
        vscode=not status.editor,
        python=not status.managed_python,
        # Default on whenever an editor exists or VS Code will be installed.
        python_extension=True,
    )
```

</details>

## 🔧 Function `detect_status`

```python
def detect_status(*, python_version: str = '3.13') -> DetectionStatus
```

Detect Git, uv, editor, and managed Python availability.

<details>
<summary>Code:</summary>

```python
def detect_status(*, python_version: str = "3.13") -> DetectionStatus:
    refresh_path()
    git = command_exists("git")
    uv = find_uv_exe()
    managed = False
    if uv is not None:
        managed = managed_python_exists(uv, python_version)
    return DetectionStatus(
        git=git,
        uv=uv is not None,
        editor=any_code_editor_exists(),
        managed_python=managed,
        git_path=shutil.which("git"),
        uv_path=str(uv) if uv else None,
    )
```

</details>

## 🔧 Function `ensure_managed_python`

```python
def ensure_managed_python(*, version: str, deps: Path, log: OutcomeLog, state: dict[str, bool]) -> None
```

Install or verify managed Python via `uv python install`.

<details>
<summary>Code:</summary>

```python
def ensure_managed_python(
    *,
    version: str,
    deps: Path,
    log: OutcomeLog,
    state: dict[str, bool],
) -> None:
    uv = find_uv_exe()
    if uv is None:
        msg = "uv was not found; cannot install managed Python"
        raise RuntimeError(msg)
    had_before = managed_python_exists(uv, version)
    py_cache = deps / "uv-python-cache"
    env = os.environ.copy()
    if py_cache.is_dir():
        env["UV_PYTHON_CACHE_DIR"] = str(py_cache)
        log.detail(f"Using offline uv python cache: {py_cache}")
    log.detail(f"uv python install {version}")
    cmd = [str(uv), "python", "install", version]
    if py_cache.is_dir():
        offline = subprocess.run(
            [*cmd, "--offline"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if offline.stdout.strip():
            log.detail(offline.stdout.strip()[:2000])
        if offline.returncode != 0:
            log.detail("uv python install --offline failed; retrying online…")
            proc = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        else:
            proc = offline
    else:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    if proc.stdout.strip():
        log.detail(proc.stdout.strip()[:2000])
    if proc.stderr.strip():
        log.detail(proc.stderr.strip()[:2000])
    if proc.returncode != 0:
        msg = f"uv python install {version} failed (exit {proc.returncode})"
        raise RuntimeError(msg)
    if not managed_python_exists(uv, version):
        msg = f"Managed Python {version} not found after install"
        raise RuntimeError(msg)
    if not had_before:
        state["python_was_provisioned"] = True
        log.add("installed", f"Provisioned managed Python {version} (uv python install)")
    else:
        log.add("already", f"Managed Python {version} already installed (uv)")
```

</details>

## 🔧 Function `find_local_dependency`

```python
def find_local_dependency(deps: Path, pattern: str) -> Path | None
```

Return the first matching file under `deps`, if unique.

<details>
<summary>Code:</summary>

```python
def find_local_dependency(deps: Path, pattern: str) -> Path | None:
    if not deps.is_dir():
        return None
    matches = sorted(deps.glob(pattern))
    files = [p for p in matches if p.is_file()]
    if len(files) == 1:
        return files[0]
    if len(files) > 1:
        return files[0]
    return None
```

</details>

## 🔧 Function `find_uv_exe`

```python
def find_uv_exe() -> Path | None
```

Locate the `uv` executable on PATH or common install locations.

<details>
<summary>Code:</summary>

```python
def find_uv_exe() -> Path | None:
    which = shutil.which("uv")
    if which:
        return Path(which)
    home = Path.home()
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    pf = _program_files()
    pf86 = _program_files_x86()
    candidates = [
        home / ".local" / "bin" / "uv.exe",
        local / "Programs" / "uv" / "uv.exe",
        local / "Microsoft" / "WinGet" / "Links" / "uv.exe",
        local / "Microsoft" / "WindowsApps" / "uv.exe",
        pf / "uv" / "uv.exe",
        pf86 / "uv" / "uv.exe",
    ]
    for path in candidates:
        if path.is_file():
            return path
    return None
```

</details>

## 🔧 Function `find_winget`

```python
def find_winget() -> Path | None
```

Locate the `winget` executable on PATH or common install locations.

<details>
<summary>Code:</summary>

```python
def find_winget() -> Path | None:
    which = shutil.which("winget")
    if which:
        return Path(which)
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    candidates = [
        local / "Microsoft" / "WindowsApps" / "winget.exe",
        _program_files() / "WindowsApps" / "Microsoft.DesktopAppInstaller_*" / "winget.exe",
    ]
    for path in candidates[:1]:
        if path.is_file():
            return path
    return None
```

</details>

## 🔧 Function `install_prerequisites`

```python
def install_prerequisites(plan: PrerequisitePlan, *, deps: Path, python_version: str, log: OutcomeLog, state: dict[str, bool], allow_network: bool) -> None
```

Install selected prerequisites from bundle, winget, or download.

<details>
<summary>Code:</summary>

```python
def install_prerequisites(
    plan: PrerequisitePlan,
    *,
    deps: Path,
    python_version: str,
    log: OutcomeLog,
    state: dict[str, bool],
    allow_network: bool,
) -> None:
    if not (plan.git or plan.uv or plan.vscode or plan.python or plan.python_extension):
        log.add("skipped", "Prerequisites install skipped")
        return

    log.step("Install selected tools")
    log.detail("Order for each tool: bundled installer in this EXE, then winget, then download")
    refresh_path()

    if plan.git and not command_exists("git"):
        log.step("Installing Git")
        git_installer = find_local_dependency(deps, "Git-*-64-bit.exe") or find_local_dependency(deps, GIT_EXE_NAME)
        ok = False
        if git_installer:
            log.detail(f"Running bundled silent installer: {git_installer.name}")
            ok = run_silent_setup(
                git_installer,
                ["/VERYSILENT", "/NORESTART", "/SUPPRESSMSGBOXES"],
                log,
            )
            refresh_path()
        if not ok and allow_network:
            log.detail("Bundled Git installer missing or failed; trying winget")
            try:
                winget_install(GIT_WINGET_ID, log)
            except RuntimeError as exc:
                log.detail(str(exc))
                _download_and_install_git(deps, log)
            refresh_path()
        if command_exists("git"):
            log.add("installed", "Installed Git" + (" (offline)" if git_installer and ok else ""))
        else:
            log.add("failed", "Git install failed")
    elif command_exists("git"):
        log.add("already", "Git already installed")
    elif not plan.git:
        log.add("skipped", "Git install skipped by user")

    if plan.vscode and not any_code_editor_exists():
        log.step("Installing VS Code")
        vs = find_local_dependency(deps, "VSCode*Setup*x64*.exe") or find_local_dependency(deps, VSCODE_EXE_NAME)
        ok = False
        if vs:
            log.detail(f"Running bundled silent installer: {vs.name}")
            ok = run_silent_setup(
                vs,
                [
                    "/VERYSILENT",
                    "/NORESTART",
                    "/MERGETASKS=!runcode,addcontextmenufiles,addcontextmenufolders,addtopath",
                ],
                log,
            )
            refresh_path()
        if not ok and allow_network:
            log.detail("Bundled VS Code installer missing or failed; trying winget, then download")
            try:
                winget_install(VSCODE_WINGET_ID, log)
            except RuntimeError as exc:
                log.detail(str(exc))
                _download_and_install_vscode(deps, log)
            refresh_path()
        if any_code_editor_exists():
            log.add("installed", "Installed VS Code" + (" (offline)" if vs and ok else ""))
        else:
            log.add("failed", "VS Code install failed")
    elif any_code_editor_exists():
        log.add("already", "Cursor/VS Code already installed")
    elif not plan.vscode:
        log.add("skipped", "VS Code install skipped by user")

    if plan.uv and find_uv_exe() is None:
        log.step("Installing uv")
        uv_zip = find_local_dependency(deps, UV_WINDOWS_ZIP)
        installed = False
        if uv_zip:
            try:
                log.detail(f"Extracting bundled {uv_zip.name} into %USERPROFILE%\\.local\\bin")
                install_uv_from_zip(uv_zip, log)
                installed = True
                log.add("installed", "Installed uv from the bundled zip")
            except RuntimeError as exc:
                log.detail(str(exc))
        if not installed and allow_network:
            log.detail("Bundled uv zip missing or failed; trying winget, then the official install script")
            try:
                winget_install(UV_WINGET_ID, log)
                refresh_path()
            except RuntimeError:
                log.detail("winget uv failed; trying official install script…")
                powershell = shutil.which("powershell.exe") or shutil.which("powershell")
                if powershell:
                    subprocess.run(
                        [
                            powershell,
                            "-NoProfile",
                            "-ExecutionPolicy",
                            "Bypass",
                            "-Command",
                            "irm https://astral.sh/uv/install.ps1 | iex",
                        ],
                        check=False,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                refresh_path()
            if find_uv_exe():
                log.add("installed", "Installed uv")
            else:
                log.add("failed", "uv install failed")
        elif not installed:
            log.add("failed", "uv install failed (offline)")
    elif find_uv_exe():
        log.add("already", "uv already installed")
    elif not plan.uv:
        log.add("skipped", "uv install skipped by user")

    refresh_path()
    if plan.python:
        log.step("Installing managed Python")
        log.detail(f"uv python install {python_version} (uses bundled uv-python-cache when present)")
        ensure_managed_python(version=python_version, deps=deps, log=log, state=state)
    else:
        log.add("skipped", "Managed Python install skipped by user")

    refresh_path()
    if plan.python_extension:
        from harrix_swiss_knife.installer.vscode_ext import install_vscode_python_extension  # noqa: PLC0415

        install_vscode_python_extension(deps=deps, log=log, allow_network=allow_network)
    else:
        log.add("skipped", "Python extension install skipped by user")
```

</details>

## 🔧 Function `install_uv_from_zip`

```python
def install_uv_from_zip(zip_path: Path, log: OutcomeLog) -> None
```

Install uv from a bundled Windows zip into `~/.local/bin`.

<details>
<summary>Code:</summary>

```python
def install_uv_from_zip(zip_path: Path, log: OutcomeLog) -> None:
    bin_dir = Path.home() / ".local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    installed: list[str] = []
    with tempfile.TemporaryDirectory(prefix="hsk-uv-") as tmp:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp)
        root = Path(tmp)
        for name in ("uv.exe", "uvx.exe", "uvw.exe"):
            hits = list(root.rglob(name))
            if hits:
                shutil.copy2(hits[0], bin_dir / name)
                installed.append(name)
    if not installed:
        msg = f"uv zip missing binaries: {zip_path}"
        raise RuntimeError(msg)
    _ensure_user_path_prepend(bin_dir)
    refresh_path()
    receipt_home = Path(os.environ.get("LOCALAPPDATA", "")) / "uv"
    receipt_home.mkdir(parents=True, exist_ok=True)
    ver = "unknown"
    uv = find_uv_exe()
    if uv:
        try:
            out = subprocess.run(
                [str(uv), "--version"],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            match = re.search(r"uv\s+([0-9]+\.[0-9]+\.[0-9]+)", out.stdout or "")
            if match:
                ver = match.group(1)
        except OSError:
            pass
    receipt = {
        "binaries": installed,
        "binary_aliases": {},
        "cdylibs": [],
        "cstaticlibs": [],
        "install_layout": "flat",
        "install_prefix": str(bin_dir),
        "modify_path": True,
        "provider": {"source": "cargo-dist", "version": "unknown"},
        "source": {"app_name": "uv", "name": "uv", "owner": "astral-sh", "release_type": "github"},
        "version": ver,
    }
    (receipt_home / "uv-receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    if find_uv_exe() is None:
        msg = "uv installed but not found on PATH"
        raise RuntimeError(msg)
    log.detail(f"Installed uv binaries into {bin_dir}")
```

</details>

## 🔧 Function `managed_python_exists`

```python
def managed_python_exists(uv_exe: Path, version: str) -> bool
```

Return whether uv has a managed CPython matching `version`.

<details>
<summary>Code:</summary>

```python
def managed_python_exists(uv_exe: Path, version: str) -> bool:
    try:
        proc = subprocess.run(
            [str(uv_exe), "python", "dir"],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except OSError:
        return False
    line = (proc.stdout or "").splitlines()
    if not line:
        return False
    py_dir = Path(line[0].strip())
    if not py_dir.is_dir():
        return False
    return any(p.is_dir() and p.name.startswith(f"cpython-{version}") for p in py_dir.iterdir())
```

</details>

## 🔧 Function `refresh_path`

```python
def refresh_path() -> None
```

Refresh process PATH from the environment and Windows registry.

<details>
<summary>Code:</summary>

```python
def refresh_path() -> None:
    machine = os.environ.get("Path", "")  # noqa: SIM112
    user = ""
    if winreg is not None:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                user, _ = winreg.QueryValueEx(key, "Path")
        except OSError:
            user = os.environ.get("Path", "")  # noqa: SIM112
    else:
        user = os.environ.get("Path", "")  # noqa: SIM112
    parts = [p for p in (machine, user) if p]
    if winreg is not None:
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            ) as key:
                machine_reg, _ = winreg.QueryValueEx(key, "Path")
                parts = [machine_reg, user]
        except OSError:
            pass
    os.environ["Path"] = ";".join(parts)  # noqa: SIM112
```

</details>

## 🔧 Function `run_silent_setup`

```python
def run_silent_setup(path: Path, args: list[str], log: OutcomeLog) -> bool
```

Run an installer executable silently and return whether it succeeded.

<details>
<summary>Code:</summary>

```python
def run_silent_setup(path: Path, args: list[str], log: OutcomeLog) -> bool:
    log.detail(f"Running {path.name} …")
    try:
        proc = subprocess.run(
            [str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except OSError as exc:
        log.detail(f"Installer failed: {exc}")
        return False
    if proc.stdout.strip():
        log.detail(proc.stdout.strip()[:2000])
    return proc.returncode == 0
```

</details>

## 🔧 Function `winget_install`

```python
def winget_install(package_id: str, log: OutcomeLog) -> None
```

Install a package silently via winget.

<details>
<summary>Code:</summary>

```python
def winget_install(package_id: str, log: OutcomeLog) -> None:
    winget = find_winget()
    if winget is None:
        msg = "winget not found"
        raise RuntimeError(msg)
    log.detail(f"winget install --id {package_id}")
    proc = subprocess.run(
        [
            str(winget),
            "install",
            "-e",
            "--id",
            package_id,
            "--source",
            "winget",
            "--accept-package-agreements",
            "--accept-source-agreements",
            "--silent",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    text = "\n".join(filter(None, [proc.stdout.strip(), proc.stderr.strip()]))
    if text:
        log.detail(text[:3000])
    if proc.returncode == 0:
        return
    ok_markers = (
        "already installed",
        "No available upgrade",
        "No newer package",
        "successfully installed",
        "Nothing to do",
    )
    if any(m.lower() in text.lower() for m in ok_markers):
        return
    msg = f"winget install {package_id} failed (exit {proc.returncode})"
    raise RuntimeError(msg)
```

</details>
