---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pack_exes.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_payload_zips`](#-function-build_payload_zips)
- [🔧 Function `ensure_installer_stub`](#-function-ensure_installer_stub)
- [🔧 Function `pack_installer_exes`](#-function-pack_installer_exes)
- [🔧 Function `stub_dir`](#-function-stub_dir)
- [🔧 Function `stub_exe_path`](#-function-stub_exe_path)

</details>

## 🔧 Function `build_payload_zips`

```python
def build_payload_zips(project_root: Path, log: LogFn, *, copy_deps_fn: Callable[..., None], online_exclude_dirs: frozenset[str], omit_files: set[str]) -> tuple[Path, Path]
```

Create temporary online/offline zips containing only `dependencies/`.

<details>
<summary>Code:</summary>

```python
def build_payload_zips(
    project_root: Path,
    log: LogFn,
    *,
    copy_deps_fn: Callable[..., None],
    online_exclude_dirs: frozenset[str],
    omit_files: set[str],
) -> tuple[Path, Path]:
    deps = project_root / "install" / "dependencies"
    if not deps.is_dir():
        msg = f"Not found: {deps}"
        raise FileNotFoundError(msg)

    stage_base = Path(tempfile.mkdtemp(prefix="hsk-payload-zip-"))
    try:
        online_stage = stage_base / "online"
        offline_stage = stage_base / "offline"
        online_stage.mkdir()
        offline_stage.mkdir()
        copy_deps_fn(
            deps,
            online_stage / "dependencies",
            exclude_dirs=online_exclude_dirs,
            exclude_files=omit_files,
        )
        copy_deps_fn(
            deps,
            offline_stage / "dependencies",
            exclude_dirs=frozenset(),
            exclude_files=omit_files,
        )
        meta = collect_build_meta(project_root)
        write_build_meta(online_stage / "build_meta.json", meta)
        write_build_meta(offline_stage / "build_meta.json", meta)
        online_zip = stage_base / "online-payload.zip"
        offline_zip = stage_base / "offline-payload.zip"
        _zip_tree(online_stage, online_zip)
        _zip_tree(offline_stage, offline_zip)
        # Move zips next to install for append (keep until pack finishes)
        install = project_root / "install"
        out_online = install / ".payload-online.zip"
        out_offline = install / ".payload-offline.zip"
        shutil.copy2(online_zip, out_online)
        shutil.copy2(offline_zip, out_offline)
        log(f"  Payload zips: {out_online.name}, {out_offline.name}")
        return out_online, out_offline
    finally:
        shutil.rmtree(stage_base, ignore_errors=True)
```

</details>

## 🔧 Function `ensure_installer_stub`

```python
def ensure_installer_stub(project_root: Path, log: LogFn, *, force: bool = False) -> Path
```

Freeze the GUI installer stub once (reused across online/offline packs).

<details>
<summary>Code:</summary>

```python
def ensure_installer_stub(project_root: Path, log: LogFn, *, force: bool = False) -> Path:
    out = stub_exe_path(project_root)
    version_file = stub_dir(project_root) / "stub-version.txt"
    stale = (not version_file.is_file()) or version_file.read_text(encoding="utf-8").strip() != STUB_SPEC_VERSION
    if out.is_file() and not force and not stale:
        log(f"  Reusing installer stub: {out}")
        return out

    if shutil.which("pyinstaller") is None and not _module_available("PyInstaller"):
        msg = "PyInstaller is required. Install with: uv sync --group dev"
        raise RuntimeError(msg)

    work = stub_dir(project_root)
    work.mkdir(parents=True, exist_ok=True)
    dist = work / "dist"
    build = work / "build"
    dist.mkdir(exist_ok=True)
    build.mkdir(exist_ok=True)

    # Entry script that only imports the installer package (not the tray app).
    entry = work / "stub_main.py"
    entry.write_text(
        "from harrix_swiss_knife.installer.wizard import main\n\nif __name__ == '__main__':\n    main()\n",
        encoding="utf-8",
    )

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        STUB_EXE_NAME.removesuffix(".exe"),
        "--distpath",
        str(dist),
        "--workpath",
        str(build),
        "--specpath",
        str(work),
        "--paths",
        str(project_root / "src"),
    ]
    icon = project_root / "src" / "harrix_swiss_knife" / "assets" / "app.ico"
    padded_ico = work / "app-padded.ico"
    if icon.is_file():
        try:
            write_padded_ico(padded_ico)
            icon_for_exe = padded_ico
        except Exception as exc:
            log(f"  Could not rebuild padded ICO ({exc}); using app.ico as-is")
            icon_for_exe = icon
        cmd.extend(["--icon", str(icon_for_exe)])
        cmd.extend(["--add-data", f"{icon}{os.pathsep}harrix_swiss_knife/assets"])
    logo = find_logo_svg() or (project_root / "src" / "harrix_swiss_knife" / "assets" / "logo.svg")
    if logo.is_file():
        cmd.extend(["--add-data", f"{logo}{os.pathsep}harrix_swiss_knife/assets"])
    cmd.extend(
        [
            "--collect-all",
            "PySide6",
            "--collect-data",
            "certifi",
            "--collect-submodules",
            "harrix_swiss_knife.installer",
            "--hidden-import",
            "harrix_swiss_knife.desktop_shortcut",
            "--hidden-import",
            "harrix_swiss_knife.integrations.http_download",
            "--hidden-import",
            "harrix_swiss_knife.integrations.http_transport",
            "--hidden-import",
            "clr",
            "--hidden-import",
            "pythonnet",
            "--exclude-module",
            "harrix_pylib",
            "--exclude-module",
            "harrix_pyssg",
            "--exclude-module",
            "harrix_swiss_knife.actions",
            "--exclude-module",
            "harrix_swiss_knife.apps",
            "--exclude-module",
            "harrix_swiss_knife.integrations.ai",
            "--exclude-module",
            "harrix_swiss_knife.integrations.bothub_client",
            str(entry),
        ]
    )
    log("==> Freeze installer stub (PyInstaller one-file)")
    log(f"  $ {' '.join(cmd)}")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src") + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        cmd,
        cwd=str(project_root),
        env=env,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    if proc.stdout.strip():
        log(proc.stdout.strip()[-4000:])
    if proc.stderr.strip():
        log(proc.stderr.strip()[-4000:])
    if proc.returncode != 0 or not out.is_file():
        msg = f"PyInstaller failed (exit {proc.returncode}); stub missing at {out}"
        raise RuntimeError(msg)
    version_file.write_text(STUB_SPEC_VERSION, encoding="utf-8")
    log(f"✅ Stub ready: {out}")
    return out
```

</details>

## 🔧 Function `pack_installer_exes`

```python
def pack_installer_exes(project_root: Path, online_zip: Path, offline_zip: Path, log: LogFn, *, force_stub: bool = False) -> tuple[Path, Path]
```

Append payload zips to the stub; write online/offline EXEs under `install/`.

<details>
<summary>Code:</summary>

```python
def pack_installer_exes(
    project_root: Path,
    online_zip: Path,
    offline_zip: Path,
    log: LogFn,
    *,
    force_stub: bool = False,
) -> tuple[Path, Path]:
    stub = ensure_installer_stub(project_root, log, force=force_stub)
    install = project_root / "install"
    online_exe = install / ONLINE_EXE_NAME
    offline_exe = install / OFFLINE_EXE_NAME
    log(f"==> Pack installer EXEs\n  {online_exe}\n  {offline_exe}")
    append_overlay_zip(stub, online_zip, online_exe)
    log(f"✅ Created: {online_exe} ({online_exe.stat().st_size // (1024 * 1024)} MB)")
    append_overlay_zip(stub, offline_zip, offline_exe)
    log(f"✅ Created: {offline_exe} ({offline_exe.stat().st_size // (1024 * 1024)} MB)")
    return online_exe, offline_exe
```

</details>

## 🔧 Function `stub_dir`

```python
def stub_dir(project_root: Path) -> Path
```

Return the PyInstaller stub working directory.

<details>
<summary>Code:</summary>

```python
def stub_dir(project_root: Path) -> Path:
    return project_root / "install" / ".installer-stub"
```

</details>

## 🔧 Function `stub_exe_path`

```python
def stub_exe_path(project_root: Path) -> Path
```

Return the built stub executable path.

<details>
<summary>Code:</summary>

```python
def stub_exe_path(project_root: Path) -> Path:
    return stub_dir(project_root) / "dist" / STUB_EXE_NAME
```

</details>
