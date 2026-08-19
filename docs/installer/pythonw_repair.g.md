---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `pythonw_repair.py`

## 🔧 Function `repair_pythonw_launcher`

```python
def repair_pythonw_launcher(project_root: Path, log: OutcomeLog) -> None
```

Replace venv `pythonw.exe` with the managed GUI launcher when needed.

<details>
<summary>Code:</summary>

```python
def repair_pythonw_launcher(project_root: Path, log: OutcomeLog) -> None:
    log.step("Repair pythonw.exe launcher (uv #19226)")
    cfg = project_root / ".venv" / "pyvenv.cfg"
    target = project_root / ".venv" / "Scripts" / "pythonw.exe"
    home = _pyvenv_home(cfg)
    if not home:
        log.add("skipped", "pythonw.exe repair skipped (pyvenv.cfg home missing)")
        return
    source = Path(home) / "pythonw.exe"
    if not source.is_file():
        log.add("skipped", "pythonw.exe repair skipped (managed pythonw.exe missing)")
        return
    if _pe_subsystem(source) != _GUI_SUBSYSTEM:
        log.add("skipped", "pythonw.exe repair skipped (managed launcher is not GUI)")
        return
    if not target.is_file():
        log.add("skipped", "pythonw.exe repair skipped (venv pythonw.exe missing)")
        return
    if _pe_subsystem(target) == _GUI_SUBSYSTEM:
        log.add("skipped", "pythonw.exe repair skipped (already GUI launcher)")
        return
    broken = target.with_name("pythonw.exe.broken")
    for stale in (broken, Path(str(broken) + ".old")):
        stale.unlink(missing_ok=True)
    try:
        shutil.copy2(source, target)
    except OSError:
        try:
            target.rename(broken)
            shutil.copy2(source, target)
        except OSError as exc:
            if broken.is_file() and not target.exists():
                broken.rename(target)
            log.add("failed", f"pythonw.exe repair failed: {exc}")
            return
    if _pe_subsystem(target) != _GUI_SUBSYSTEM:
        log.add("failed", "pythonw.exe repair failed (launcher still not GUI)")
        return
    log.add("installed", "Repaired pythonw.exe launcher (uv #19226 workaround)")
```

</details>
