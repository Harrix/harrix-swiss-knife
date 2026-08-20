---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `deploy.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DeployOptions`](#%EF%B8%8F-class-deployoptions)
- [🏛️ Class `DeployResult`](#%EF%B8%8F-class-deployresult)
- [🔧 Function `pinned_python_version`](#-function-pinned_python_version)
- [🔧 Function `run_deploy`](#-function-run_deploy)
- [🔧 Function `suggest_install_root`](#-function-suggest_install_root)

</details>

## 🏛️ Class `DeployOptions`

```python
class DeployOptions
```

User choices for a deploy run.

<details>
<summary>Code:</summary>

```python
class DeployOptions:

    mode: str  # "online" | "offline"
    install_root: Path
    plan: PrerequisitePlan
    desktop_shortcut: bool = True
    startup_shortcut: bool = True
    deps_dir: Path | None = None
    python_version: str = "3.13"
    allow_network: bool = True
```

</details>

## 🏛️ Class `DeployResult`

```python
class DeployResult
```

Outcome of [`run_deploy`](#-function-run_deploy).

<details>
<summary>Code:</summary>

```python
class DeployResult:

    ok: bool
    install_root: Path | None
    hsk_path: Path | None
    outcomes: OutcomeLog
    error: str | None = None
    elapsed_seconds: float = 0.0
```

</details>

## 🔧 Function `pinned_python_version`

```python
def pinned_python_version(deps: Path | None = None, hsk_hint: Path | None = None) -> str
```

Return pinned Python version from `.python-version` or default `3.13`.

<details>
<summary>Code:</summary>

```python
def pinned_python_version(deps: Path | None = None, hsk_hint: Path | None = None) -> str:
    for candidate in (
        hsk_hint / ".python-version" if hsk_hint else None,
        deps.parent / ".python-version" if deps else None,
    ):
        if candidate is not None and candidate.is_file():
            line = candidate.read_text(encoding="utf-8").splitlines()
            if line and line[0].strip():
                return line[0].strip()
    return "3.13"
```

</details>

## 🔧 Function `run_deploy`

```python
def run_deploy(options: DeployOptions, log: OutcomeLog) -> DeployResult
```

Run the full install pipeline.

<details>
<summary>Code:</summary>

```python
def run_deploy(options: DeployOptions, log: OutcomeLog) -> DeployResult:
    started = time.perf_counter()
    state = {"python_was_provisioned": False}
    offline = options.mode.lower() == "offline"
    allow_network = options.allow_network and not offline
    deps = options.deps_dir
    if deps is None or not deps.is_dir():
        return DeployResult(
            ok=False,
            install_root=None,
            hsk_path=None,
            outcomes=log,
            error="dependencies folder missing (payload not extracted)",
            elapsed_seconds=time.perf_counter() - started,
        )

    try:
        mode_label = "Offline (bundle first, network only if something is missing)"
        if not offline:
            mode_label = "Online (clone from GitHub; use bundled installers when present)"
        log.step(f"Install mode: {mode_label}")
        py_ver = options.python_version or pinned_python_version(deps)
        status = detect_status(python_version=py_ver)
        log.detail(
            f"Detected on this PC: Git={'yes' if status.git else 'no'}, "
            f"uv={'yes' if status.uv else 'no'}, "
            f"editor={'yes' if status.editor else 'no'}, "
            f"managed Python={'yes' if status.managed_python else 'no'}"
        )

        install_prerequisites(
            options.plan,
            deps=deps,
            python_version=py_ver,
            log=log,
            state=state,
            allow_network=allow_network,
        )

        root = normalize_install_root(options.install_root)
        root.mkdir(parents=True, exist_ok=True)
        log.step("Create install folder")
        log.detail(f"Repos will live under {root} (harrix-pylib, harrix-pyssg, harrix-swiss-knife)")
        repair_install_tree_acls(root, log)

        hsk = ensure_repos(root, deps=deps, offline=offline, log=log)

        if state.get("python_was_provisioned"):
            log.step("Reset harrix-swiss-knife venv (Python was provisioned)")
            venv = hsk / ".venv"
            if venv.exists():
                shutil.rmtree(venv)
                log.add("installed", "Removed harrix-swiss-knife .venv after Python provisioning")
            else:
                log.add("already", "harrix-swiss-knife .venv not present (no reset needed)")

        for name in ("harrix-pylib", "harrix-pyssg", "harrix-swiss-knife"):
            path = root / name
            log.step(f"Install Python packages ({name})")
            used = uv_sync_with_bundle_cache(path, deps=deps, label=name, log=log)
            how = "bundled uv-cache (offline)" if used else "uv download from the network"
            log.add("installed", f"uv sync finished for {name} via {how}")

        if not repair_install_tree_acls(root, log):
            _raise_acl_repair_failed()
        ensure_runtime_imports(hsk, log=log)

        install_hsk_cli(hsk, log)
        apply_config_defaults(hsk, log)
        repair_pythonw_launcher(hsk, log)

        if options.desktop_shortcut:
            log.step("Desktop shortcut")
            try:
                create_desktop_shortcut(hsk)
                log.add("installed", "Desktop shortcut created")
            except OSError as exc:
                log.add("failed", f"Desktop shortcut failed: {exc}")

        if options.startup_shortcut:
            log.step("Windows autostart (Startup folder)")
            try:
                create_startup_shortcut(hsk)
                log.add("installed", "Startup shortcut created")
            except OSError as exc:
                log.add("failed", f"Startup shortcut failed: {exc}")

        removed_lnk = remove_desktop_uninstall_shortcut()
        if removed_lnk is not None:
            log.add("installed", f"Removed legacy desktop uninstall shortcut ({removed_lnk.name})")

        try:
            install_optimize_binaries(hsk, deps=deps, skip_download=offline, log=log)
        except Exception as exc:
            log.add("failed", f"Optimize binaries install failed: {exc}")

        meta = load_build_meta()
        register_uninstall(
            install_root=root,
            hsk_path=hsk,
            version=meta.get("version") or "unknown",
            log=log,
        )

        # Keep a durable copy of the install log next to the app.
        try:
            if log._file is not None and log._file.is_file():  # noqa: SLF001
                dest_log = hsk / "install.log"
                shutil.copy2(log._file, dest_log)  # noqa: SLF001
                log.detail(f"Copied install log to {dest_log}")
        except OSError as exc:
            log.detail(f"Could not copy install.log: {exc}")

        log.step("Done")
        pyw = hsk / ".venv" / "Scripts" / "pythonw.exe"
        launch_py = hsk / "launch_tray.py"
        log.line("")
        log.line(f"Install root:    {root}")
        log.line(f'Run tray app:    "{pyw}" "{launch_py}"')
        log.line(f'Uninstall:       "{pyw}" "{hsk / "launch_uninstall.py"}"')
        log.line("CLI examples:    hsk md --help")
        for line in log.summary_lines():
            log.line(line)
        elapsed = time.perf_counter() - started
        log.line(f"\n⏱️ Elapsed: {elapsed:0.1f}s")
        return DeployResult(
            ok=True,
            install_root=root,
            hsk_path=hsk,
            outcomes=log,
            elapsed_seconds=elapsed,
        )
    except Exception as exc:
        log.line(f"❌ ERROR: {exc}")
        return DeployResult(
            ok=False,
            install_root=None,
            hsk_path=None,
            outcomes=log,
            error=str(exc),
            elapsed_seconds=time.perf_counter() - started,
        )
```

</details>

## 🔧 Function `suggest_install_root`

```python
def suggest_install_root() -> Path
```

Return the default install parent folder.

<details>
<summary>Code:</summary>

```python
def suggest_install_root() -> Path:
    return default_install_root_parent()
```

</details>
