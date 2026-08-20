---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `create_desktop_shortcut.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnCreateDesktopShortcut`](#%EF%B8%8F-class-oncreatedesktopshortcut)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnCreateDesktopShortcut`

```python
class OnCreateDesktopShortcut(ActionBase)
```

Create or update a desktop shortcut to launch Harrix Swiss Knife.

Uses the same target, arguments, working directory, and icon as the GUI
installer (`pythonw.exe`, `main.py`, `assets/app.ico` or legacy
`img/icon.ico`). Before creating the shortcut, repairs
`.venv\Scripts\pythonw.exe` when uv creates a console launcher
(<https://github.com/astral-sh/uv/issues/19226>). After `uv sync`,
rerun this action if a console window appears on startup. Windows only.

<details>
<summary>Code:</summary>

```python
class OnCreateDesktopShortcut(ActionBase):

    icon = "🔗"
    title = "Create desktop shortcut"

    @ActionBase.handle_exceptions("creating desktop shortcut")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Create desktop shortcut for this project."""
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return

        project_root = h.dev.get_project_root()
        scripts = project_root / ".venv" / "Scripts"
        gui_exe = scripts / "harrix-swiss-knife.exe"
        pyw = scripts / "pythonw.exe"
        launch_py = project_root / "launch_tray.py"
        main_py = project_root / "src" / "harrix_swiss_knife" / "main.py"
        has_script_launch = pyw.is_file() and (launch_py.is_file() or main_py.is_file())

        if not gui_exe.is_file() and not has_script_launch:
            if not pyw.is_file():
                self.add_line(f"❌ pythonw.exe not found: {pyw}")
            else:
                self.add_line(f"❌ launch_tray.py / main.py not found under {project_root}")
            self.show_result()
            return

        repair = fix_pythonw_launcher(project_root)
        for line in repair.details:
            self.add_line(line)

        if repair.status == "fixed":
            self.add_line(f"✅ {repair.message}")
        elif repair.status == "already_ok":
            self.add_line(f"OK: {repair.message}")
        elif repair.status == "skipped":
            self.add_line(f"⚠️ {repair.message}")
        else:
            self.add_line(f"❌ {repair.message}")
            self.show_result()
            return

        try:
            lnk_path = create_desktop_shortcut(project_root)
        except OSError as e:
            self.add_line(f"❌ {e}")
            self.show_result()
            return

        self.add_line(f"✅ Desktop shortcut created: {lnk_path}")
        self.show_toast("Desktop shortcut created")
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Create desktop shortcut for this project.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if sys.platform != "win32":
            self.add_line("This action is only available on Windows.")
            self.show_result()
            return

        project_root = h.dev.get_project_root()
        scripts = project_root / ".venv" / "Scripts"
        gui_exe = scripts / "harrix-swiss-knife.exe"
        pyw = scripts / "pythonw.exe"
        launch_py = project_root / "launch_tray.py"
        main_py = project_root / "src" / "harrix_swiss_knife" / "main.py"
        has_script_launch = pyw.is_file() and (launch_py.is_file() or main_py.is_file())

        if not gui_exe.is_file() and not has_script_launch:
            if not pyw.is_file():
                self.add_line(f"❌ pythonw.exe not found: {pyw}")
            else:
                self.add_line(f"❌ launch_tray.py / main.py not found under {project_root}")
            self.show_result()
            return

        repair = fix_pythonw_launcher(project_root)
        for line in repair.details:
            self.add_line(line)

        if repair.status == "fixed":
            self.add_line(f"✅ {repair.message}")
        elif repair.status == "already_ok":
            self.add_line(f"OK: {repair.message}")
        elif repair.status == "skipped":
            self.add_line(f"⚠️ {repair.message}")
        else:
            self.add_line(f"❌ {repair.message}")
            self.show_result()
            return

        try:
            lnk_path = create_desktop_shortcut(project_root)
        except OSError as e:
            self.add_line(f"❌ {e}")
            self.show_result()
            return

        self.add_line(f"✅ Desktop shortcut created: {lnk_path}")
        self.show_toast("Desktop shortcut created")
        self.show_result()
```

</details>
