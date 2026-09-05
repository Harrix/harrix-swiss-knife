---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `close_all_adobe.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCloseAllAdobe`](#%EF%B8%8F-class-onclosealladobe)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)
  - [⚙️ Method `in_thread`](#%EF%B8%8F-method-in_thread)
  - [⚙️ Method `thread_after`](#%EF%B8%8F-method-thread_after)

</details>

## 🏛️ Class `OnCloseAllAdobe`

```python
class OnCloseAllAdobe(ActionBase)
```

Force-close Adobe applications and Creative Cloud helpers on Windows.

Matches processes whose executable path contains `Adobe`, or whose name
starts with `Adobe` / contains `Creative Cloud`, then stops them with
`Stop-Process -Force`.

<details>
<summary>Code:</summary>

```python
class OnCloseAllAdobe(ActionBase):

    icon = "🛑"
    title = "Close all Adobe apps"
    quick_launcher = True

    @ActionBase.handle_exceptions("closing Adobe apps")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Force-close matching Adobe processes on Windows."""
        if sys.platform != "win32":
            self.add_line("❌ Windows only.")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)

    @ActionBase.handle_exceptions("closing Adobe apps thread")
    def in_thread(self) -> None:
        """Find and force-stop Adobe-related processes via PowerShell."""
        script = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { "
            "  ($_.ExecutablePath -and ($_.ExecutablePath -match '(?i)[/\\\\]Adobe[/\\\\]')) -or "
            "  ($_.Name -match '(?i)^Adobe') -or "
            "  ($_.Name -match '(?i)Creative Cloud') "
            "} | ForEach-Object { "
            "  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; "
            "  Write-Output ('Stopped PID ' + $_.ProcessId + ' (' + $_.Name + ')') "
            "}"
        )
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.add_line("❌ PowerShell not found.")
            return
        proc = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            **hidden_subprocess_kwargs(),
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if out:
            self.add_line(out)
        else:
            self.add_line("(no matching Adobe processes)")
        if err:
            self.add_line(err)

    @ActionBase.handle_exceptions("closing Adobe apps completion")
    def thread_after(self, result: Any) -> None:  # noqa: ARG002
        """Show toast and result dialog after processes are stopped."""
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Force-close matching Adobe processes on Windows.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("❌ Windows only.")
            self.show_result()
            return
        self.start_thread(self.in_thread, self.thread_after, self.title)
```

</details>

### ⚙️ Method `in_thread`

```python
def in_thread(self) -> None
```

Find and force-stop Adobe-related processes via PowerShell.

<details>
<summary>Code:</summary>

```python
def in_thread(self) -> None:
        script = (
            "Get-CimInstance Win32_Process | "
            "Where-Object { "
            "  ($_.ExecutablePath -and ($_.ExecutablePath -match '(?i)[/\\\\]Adobe[/\\\\]')) -or "
            "  ($_.Name -match '(?i)^Adobe') -or "
            "  ($_.Name -match '(?i)Creative Cloud') "
            "} | ForEach-Object { "
            "  Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; "
            "  Write-Output ('Stopped PID ' + $_.ProcessId + ' (' + $_.Name + ')') "
            "}"
        )
        powershell = shutil.which("powershell") or shutil.which("pwsh")
        if powershell is None:
            self.add_line("❌ PowerShell not found.")
            return
        proc = subprocess.run(
            [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            **hidden_subprocess_kwargs(),
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()
        if out:
            self.add_line(out)
        else:
            self.add_line("(no matching Adobe processes)")
        if err:
            self.add_line(err)
```

</details>

### ⚙️ Method `thread_after`

```python
def thread_after(self, result: Any) -> None
```

Show toast and result dialog after processes are stopped.

<details>
<summary>Code:</summary>

```python
def thread_after(self, result: Any) -> None:  # noqa: ARG002
        self.show_toast(f"{self.title} completed")
        self.show_result()
```

</details>
