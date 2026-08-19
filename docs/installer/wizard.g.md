---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `wizard.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DonePage`](#%EF%B8%8F-class-donepage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `InstallerWizard`](#%EF%B8%8F-class-installerwizard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
- [🏛️ Class `OptionsPage`](#%EF%B8%8F-class-optionspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `install_root`](#%EF%B8%8F-method-install_root)
- [🏛️ Class `ProgressPage`](#%EF%B8%8F-class-progresspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `initializePage`](#%EF%B8%8F-method-initializepage)
  - [⚙️ Method `isComplete`](#%EF%B8%8F-method-iscomplete)
  - [⚙️ Method `validatePage`](#%EF%B8%8F-method-validatepage)
- [🏛️ Class `ToolsPage`](#%EF%B8%8F-class-toolspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `initializePage`](#%EF%B8%8F-method-initializepage-1)
  - [⚙️ Method `plan`](#%EF%B8%8F-method-plan)
- [🏛️ Class `WelcomePage`](#%EF%B8%8F-class-welcomepage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
- [🔧 Function `detect_mode_from_argv`](#-function-detect_mode_from_argv)
- [🔧 Function `load_app_icon`](#-function-load_app_icon)
- [🔧 Function `run_wizard`](#-function-run_wizard)
- [🔧 Function `main`](#-function-main)

</details>

## 🏛️ Class `DonePage`

```python
class DonePage(QWizardPage)
```

Final wizard page shown after installation completes.

<details>
<summary>Code:</summary>

```python
class DonePage(QWizardPage):

    def __init__(self) -> None:
        """Build the completion page."""
        super().__init__()
        self.setTitle("Finished")
        self.label = QLabel("Installation finished. You can close this window.")
        self.label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Build the completion page.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__()
        self.setTitle("Finished")
        self.label = QLabel("Installation finished. You can close this window.")
        self.label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
```

</details>

## 🏛️ Class `InstallerWizard`

```python
class InstallerWizard(QWizard)
```

Main installer wizard coordinating all pages.

<details>
<summary>Code:</summary>

```python
class InstallerWizard(QWizard):

    def __init__(self, mode: str) -> None:
        """Create wizard pages for the given install mode."""
        super().__init__()
        self.setWindowTitle(f"Harrix Swiss Knife — {'Offline' if mode == 'offline' else 'Online'} Installer")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(720, 520)
        icon = load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        header = header_logo_pixmap()
        if not header.isNull():
            self.setPixmap(QWizard.WizardPixmap.LogoPixmap, header)
        self.mode = mode
        self.tools_page = ToolsPage(mode)
        self.options_page = OptionsPage()
        self.progress_page = ProgressPage(mode)
        self.addPage(WelcomePage(mode))
        self.addPage(self.tools_page)
        self.addPage(self.options_page)
        self.addPage(self.progress_page)
        self.addPage(DonePage())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, mode: str) -> None
```

Create wizard pages for the given install mode.

<details>
<summary>Code:</summary>

```python
def __init__(self, mode: str) -> None:
        super().__init__()
        self.setWindowTitle(f"Harrix Swiss Knife — {'Offline' if mode == 'offline' else 'Online'} Installer")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(720, 520)
        icon = load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        header = header_logo_pixmap()
        if not header.isNull():
            self.setPixmap(QWizard.WizardPixmap.LogoPixmap, header)
        self.mode = mode
        self.tools_page = ToolsPage(mode)
        self.options_page = OptionsPage()
        self.progress_page = ProgressPage(mode)
        self.addPage(WelcomePage(mode))
        self.addPage(self.tools_page)
        self.addPage(self.options_page)
        self.addPage(self.progress_page)
        self.addPage(DonePage())
```

</details>

## 🏛️ Class `OptionsPage`

```python
class OptionsPage(QWizardPage)
```

Page for choosing install location and shortcuts.

<details>
<summary>Code:</summary>

```python
class OptionsPage(QWizardPage):

    def __init__(self) -> None:
        """Build install path and shortcut options."""
        super().__init__()
        self.setTitle("Install location")
        self.path_edit = QLineEdit(str(suggest_install_root()))
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.path_edit)
        row.addWidget(browse)
        self.desktop_cb = QCheckBox("Create desktop shortcut")
        self.desktop_cb.setChecked(True)
        self.startup_cb = QCheckBox("Add to Windows Startup")
        self.startup_cb.setChecked(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Install parent folder (repos will be cloned/extracted here):"))
        layout.addLayout(row)
        layout.addWidget(self.desktop_cb)
        layout.addWidget(self.startup_cb)

    def install_root(self) -> Path:
        """Return the selected install parent folder."""
        return Path(self.path_edit.text().strip())

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select install folder", self.path_edit.text())
        if path:
            self.path_edit.setText(path)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Build install path and shortcut options.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__()
        self.setTitle("Install location")
        self.path_edit = QLineEdit(str(suggest_install_root()))
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        row = QHBoxLayout()
        row.addWidget(self.path_edit)
        row.addWidget(browse)
        self.desktop_cb = QCheckBox("Create desktop shortcut")
        self.desktop_cb.setChecked(True)
        self.startup_cb = QCheckBox("Add to Windows Startup")
        self.startup_cb.setChecked(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Install parent folder (repos will be cloned/extracted here):"))
        layout.addLayout(row)
        layout.addWidget(self.desktop_cb)
        layout.addWidget(self.startup_cb)
```

</details>

### ⚙️ Method `install_root`

```python
def install_root(self) -> Path
```

Return the selected install parent folder.

<details>
<summary>Code:</summary>

```python
def install_root(self) -> Path:
        return Path(self.path_edit.text().strip())
```

</details>

## 🏛️ Class `ProgressPage`

```python
class ProgressPage(QWizardPage)
```

Page that runs deployment and shows live progress.

<details>
<summary>Code:</summary>

```python
class ProgressPage(QWizardPage):

    def __init__(self, mode: str) -> None:
        """Build the install progress UI."""
        super().__init__()
        self.setTitle("Installing")
        self.setSubTitle("Live status of the current step is shown below.")
        self._mode = mode
        self._worker: _Worker | None = None
        self._done = False
        self._extracting = False
        self.status_label = QLabel("Ready to install")
        status_font = QFont()
        status_font.setPointSize(11)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setWordWrap(True)
        self.detail_label = QLabel("Installation starts automatically on this page.")
        self.detail_label.setWordWrap(True)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.bar = QProgressBar()
        self.bar.setRange(0, 1)
        self.bar.setValue(0)
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.bar)
        layout.addWidget(self.log_view)
        self.setCommitPage(True)
        self.setButtonText(QWizard.WizardButton.CommitButton, "Install")

    def initializePage(self) -> None:  # noqa: N802
        """Start install as soon as this page is shown (do not wait for Install)."""
        QTimer.singleShot(0, self._begin_if_needed)

    def isComplete(self) -> bool:  # noqa: N802
        """Return whether installation has finished (enables Next after success)."""
        return self._done

    def validatePage(self) -> bool:  # noqa: N802
        """Allow leaving the page only after a successful install."""
        return self._done

    def _append(self, line: str) -> None:
        self.log_view.appendPlainText(line)
        self._update_status_from_log(line)

    def _begin_if_needed(self) -> None:
        if self._done or self._worker is not None:
            return
        wizard = self.wizard()
        if not isinstance(wizard, InstallerWizard):
            return
        plan = wizard.tools_page.plan()
        if plan.need_elevate and not is_admin():
            self.status_label.setText("Administrator permission required")
            self.detail_label.setText("Git or VS Code setup needs elevation. A UAC prompt should appear.")
            self._append("==> Requesting administrator permission")
            plan_path = write_plan_file(
                {
                    "mode": self._mode,
                    "install_root": str(wizard.options_page.install_root()),
                    "plan": {
                        "git": plan.git,
                        "uv": plan.uv,
                        "vscode": plan.vscode,
                        "python": plan.python,
                    },
                    "desktop": wizard.options_page.desktop_cb.isChecked(),
                    "startup": wizard.options_page.startup_cb.isChecked(),
                }
            )
            rc = relaunch_elevated(["--continue-plan", str(plan_path)])
            if rc <= _SHELL_EXECUTE_MAX_ERROR:
                QMessageBox.warning(self, "Elevation", f"Could not elevate (ShellExecute={rc}).")
                return
            QApplication.instance().quit()  # type: ignore[union-attr]
            return
        self._start_worker(plan)

    def _on_err(self, message: str) -> None:
        self._append(f"❌ {message}")
        self._done = True
        self.completeChanged.emit()
        QMessageBox.critical(self, "Install failed", message)
        wizard = self.wizard()
        if wizard:
            wizard.button(QWizard.WizardButton.BackButton).setEnabled(True)
            wizard.button(QWizard.WizardButton.CommitButton).setEnabled(True)

    def _on_ok(self, _result: object) -> None:
        self._done = True
        self.bar.setRange(0, 1)
        self.bar.setValue(1)
        self.completeChanged.emit()
        wizard = self.wizard()
        if wizard:
            wizard.next()

    def _on_progress(self, done: int, total: int) -> None:
        if total <= 0:
            self.bar.setRange(0, 0)
            return
        self.bar.setRange(0, total)
        self.bar.setValue(min(done, total))
        if self._extracting and total > _EXTRACT_BYTE_PROGRESS_MIN:
            done_mb = done // _BYTES_PER_MIB
            total_mb = max(total // _BYTES_PER_MIB, 1)
            self.status_label.setText("Extracting installer payload")
            self.detail_label.setText(f"Copying bundled files from this EXE: {done_mb} / {total_mb} MB")
        elif self._extracting:
            self.status_label.setText("Unpacking installer payload")
            self.detail_label.setText(f"Extracting files: {done} / {total}")

    def _start_worker(self, plan: PrerequisitePlan) -> None:
        wizard = self.wizard()
        assert isinstance(wizard, InstallerWizard)  # noqa: S101
        work = Path(tempfile.mkdtemp(prefix="hsk-install-"))
        self._extracting = True
        self.status_label.setText("Starting installation")
        self.detail_label.setText("Preparing the work folder and reading the bundled payload…")
        self.bar.setRange(0, 0)
        self._append("==> Starting installation")
        self._worker = _Worker(
            mode=self._mode,
            install_root=wizard.options_page.install_root(),
            plan=plan,
            desktop=wizard.options_page.desktop_cb.isChecked(),
            startup=wizard.options_page.startup_cb.isChecked(),
            work_dir=work,
            parent=self,
        )
        self._worker.log_line.connect(self._append)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_ok.connect(self._on_ok)
        self._worker.finished_err.connect(self._on_err)
        wizard.button(QWizard.WizardButton.BackButton).setEnabled(False)
        wizard.button(QWizard.WizardButton.CommitButton).setEnabled(False)
        self._worker.start()

    def _update_status_from_log(self, line: str) -> None:
        text = line.strip()
        if text.startswith("==> "):
            self._extracting = "extract" in text.lower()
            self.status_label.setText(text[4:])
            return
        if text.startswith("Extracting payload"):
            self._extracting = True
            self.status_label.setText("Extracting installer payload")
            self.detail_label.setText(text)
            return
        if text.startswith("    "):
            self.detail_label.setText(text.strip())
            return
        if text[:1] in {"✅", "⚠️", "❌", "i", "•"}:
            self.detail_label.setText(text)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, mode: str) -> None
```

Build the install progress UI.

<details>
<summary>Code:</summary>

```python
def __init__(self, mode: str) -> None:
        super().__init__()
        self.setTitle("Installing")
        self.setSubTitle("Live status of the current step is shown below.")
        self._mode = mode
        self._worker: _Worker | None = None
        self._done = False
        self._extracting = False
        self.status_label = QLabel("Ready to install")
        status_font = QFont()
        status_font.setPointSize(11)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setWordWrap(True)
        self.detail_label = QLabel("Installation starts automatically on this page.")
        self.detail_label.setWordWrap(True)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.bar = QProgressBar()
        self.bar.setRange(0, 1)
        self.bar.setValue(0)
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.detail_label)
        layout.addWidget(self.bar)
        layout.addWidget(self.log_view)
        self.setCommitPage(True)
        self.setButtonText(QWizard.WizardButton.CommitButton, "Install")
```

</details>

### ⚙️ Method `initializePage`

```python
def initializePage(self) -> None
```

Start install as soon as this page is shown (do not wait for Install).

<details>
<summary>Code:</summary>

```python
def initializePage(self) -> None:  # noqa: N802
        QTimer.singleShot(0, self._begin_if_needed)
```

</details>

### ⚙️ Method `isComplete`

```python
def isComplete(self) -> bool
```

Return whether installation has finished (enables Next after success).

<details>
<summary>Code:</summary>

```python
def isComplete(self) -> bool:  # noqa: N802
        return self._done
```

</details>

### ⚙️ Method `validatePage`

```python
def validatePage(self) -> bool
```

Allow leaving the page only after a successful install.

<details>
<summary>Code:</summary>

```python
def validatePage(self) -> bool:  # noqa: N802
        return self._done
```

</details>

## 🏛️ Class `ToolsPage`

```python
class ToolsPage(QWizardPage)
```

Page for selecting prerequisite tools to install.

<details>
<summary>Code:</summary>

```python
class ToolsPage(QWizardPage):

    def __init__(self, mode: str) -> None:
        """Build prerequisite checkboxes."""
        super().__init__()
        self.setTitle("Tools")
        self._mode = mode
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.git_cb = QCheckBox("Install Git")
        self.uv_cb = QCheckBox("Install uv")
        self.vscode_cb = QCheckBox("Install VS Code (if no editor found)")
        self.python_cb = QCheckBox("Install managed Python via uv")
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.git_cb)
        layout.addWidget(self.uv_cb)
        layout.addWidget(self.vscode_cb)
        layout.addWidget(self.python_cb)

    def initializePage(self) -> None:  # noqa: N802
        """Populate tool checkboxes from detected system status."""
        status = detect_status()
        plan = default_plan_from_detection(status)
        self.status_label.setText(
            "Detected:\n"
            f"  Git: {'yes' if status.git else 'not found'}"
            f"{f' ({status.git_path})' if status.git_path else ''}\n"
            f"  uv: {'yes' if status.uv else 'not found'}"
            f"{f' ({status.uv_path})' if status.uv_path else ''}\n"
            f"  Editor: {'yes' if status.editor else 'not found'}\n"
            f"  Managed Python: {'yes' if status.managed_python else 'not found'}"
        )
        self.git_cb.setChecked(plan.git)
        self.uv_cb.setChecked(plan.uv)
        self.vscode_cb.setChecked(plan.vscode)
        self.python_cb.setChecked(plan.python)

    def plan(self) -> PrerequisitePlan:
        """Return the user's selected prerequisite install plan."""
        return PrerequisitePlan(
            git=self.git_cb.isChecked(),
            uv=self.uv_cb.isChecked(),
            vscode=self.vscode_cb.isChecked(),
            python=self.python_cb.isChecked(),
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, mode: str) -> None
```

Build prerequisite checkboxes.

<details>
<summary>Code:</summary>

```python
def __init__(self, mode: str) -> None:
        super().__init__()
        self.setTitle("Tools")
        self._mode = mode
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.git_cb = QCheckBox("Install Git")
        self.uv_cb = QCheckBox("Install uv")
        self.vscode_cb = QCheckBox("Install VS Code (if no editor found)")
        self.python_cb = QCheckBox("Install managed Python via uv")
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.git_cb)
        layout.addWidget(self.uv_cb)
        layout.addWidget(self.vscode_cb)
        layout.addWidget(self.python_cb)
```

</details>

### ⚙️ Method `initializePage`

```python
def initializePage(self) -> None
```

Populate tool checkboxes from detected system status.

<details>
<summary>Code:</summary>

```python
def initializePage(self) -> None:  # noqa: N802
        status = detect_status()
        plan = default_plan_from_detection(status)
        self.status_label.setText(
            "Detected:\n"
            f"  Git: {'yes' if status.git else 'not found'}"
            f"{f' ({status.git_path})' if status.git_path else ''}\n"
            f"  uv: {'yes' if status.uv else 'not found'}"
            f"{f' ({status.uv_path})' if status.uv_path else ''}\n"
            f"  Editor: {'yes' if status.editor else 'not found'}\n"
            f"  Managed Python: {'yes' if status.managed_python else 'not found'}"
        )
        self.git_cb.setChecked(plan.git)
        self.uv_cb.setChecked(plan.uv)
        self.vscode_cb.setChecked(plan.vscode)
        self.python_cb.setChecked(plan.python)
```

</details>

### ⚙️ Method `plan`

```python
def plan(self) -> PrerequisitePlan
```

Return the user's selected prerequisite install plan.

<details>
<summary>Code:</summary>

```python
def plan(self) -> PrerequisitePlan:
        return PrerequisitePlan(
            git=self.git_cb.isChecked(),
            uv=self.uv_cb.isChecked(),
            vscode=self.vscode_cb.isChecked(),
            python=self.python_cb.isChecked(),
        )
```

</details>

## 🏛️ Class `WelcomePage`

```python
class WelcomePage(QWizardPage)
```

Introductory wizard page.

<details>
<summary>Code:</summary>

```python
class WelcomePage(QWizardPage):

    def __init__(self, mode: str) -> None:
        """Build the welcome text for the selected mode."""
        super().__init__()
        self.setTitle("Welcome")
        kind = "offline bundle" if mode == "offline" else "online from GitHub"
        version_line, built_line = display_build_lines()
        self.setSubTitle(f"{version_line}  ·  {built_line}")

        logo = QLabel()
        pixmap = welcome_logo_pixmap()
        if not pixmap.isNull():
            logo.setPixmap(pixmap)
            logo.setContentsMargins(8, 8, 16, 8)
        title = QLabel("Harrix Swiss Knife")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        meta = QLabel(f"{version_line}\n{built_line}")
        meta.setWordWrap(True)
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        text_col.addWidget(title)
        text_col.addWidget(meta)
        header = QHBoxLayout()
        header.setSpacing(12)
        if not pixmap.isNull():
            header.addWidget(logo)
        header.addLayout(text_col)
        header.addStretch(1)

        label = QLabel(
            f"This wizard installs Harrix Swiss Knife ({kind}).\n\n"
            "You can choose which tools to install, the target folder, and shortcuts."
        )
        label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addSpacing(12)
        layout.addWidget(label)
        layout.addStretch(1)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, mode: str) -> None
```

Build the welcome text for the selected mode.

<details>
<summary>Code:</summary>

```python
def __init__(self, mode: str) -> None:
        super().__init__()
        self.setTitle("Welcome")
        kind = "offline bundle" if mode == "offline" else "online from GitHub"
        version_line, built_line = display_build_lines()
        self.setSubTitle(f"{version_line}  ·  {built_line}")

        logo = QLabel()
        pixmap = welcome_logo_pixmap()
        if not pixmap.isNull():
            logo.setPixmap(pixmap)
            logo.setContentsMargins(8, 8, 16, 8)
        title = QLabel("Harrix Swiss Knife")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        meta = QLabel(f"{version_line}\n{built_line}")
        meta.setWordWrap(True)
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        text_col.addWidget(title)
        text_col.addWidget(meta)
        header = QHBoxLayout()
        header.setSpacing(12)
        if not pixmap.isNull():
            header.addWidget(logo)
        header.addLayout(text_col)
        header.addStretch(1)

        label = QLabel(
            f"This wizard installs Harrix Swiss Knife ({kind}).\n\n"
            "You can choose which tools to install, the target folder, and shortcuts."
        )
        label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addSpacing(12)
        layout.addWidget(label)
        layout.addStretch(1)
```

</details>

## 🔧 Function `detect_mode_from_argv`

```python
def detect_mode_from_argv(argv: list[str]) -> str
```

Detect online/offline mode from CLI flags or executable name.

<details>
<summary>Code:</summary>

```python
def detect_mode_from_argv(argv: list[str]) -> str:
    if "--offline" in argv:
        return "offline"
    if "--online" in argv:
        return "online"
    exe = frozen_executable().name.lower()
    if "offline" in exe:
        return "offline"
    return "online"
```

</details>

## 🔧 Function `load_app_icon`

```python
def load_app_icon() -> QIcon
```

Return a sharp padded multi-size icon for the installer window.

<details>
<summary>Code:</summary>

```python
def load_app_icon() -> QIcon:
    return make_window_icon()
```

</details>

## 🔧 Function `run_wizard`

```python
def run_wizard(argv: list[str] | None = None) -> int
```

Run the installer wizard and return the Qt exit code.

<details>
<summary>Code:</summary>

```python
def run_wizard(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    app = QApplication.instance() or QApplication(sys.argv)
    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

    if "--continue-plan" in args:
        idx = args.index("--continue-plan")
        plan_path = Path(args[idx + 1])
        data = read_plan_file(plan_path)
        mode = str(data.get("mode", "online"))
        wizard = InstallerWizard(mode)
        wizard.options_page.path_edit.setText(str(data.get("install_root", suggest_install_root())))
        wizard.options_page.desktop_cb.setChecked(bool(data.get("desktop", True)))
        wizard.options_page.startup_cb.setChecked(bool(data.get("startup", True)))
        plan_raw = data.get("plan") or {}
        wizard.tools_page.git_cb.setChecked(bool(plan_raw.get("git", True)))
        wizard.tools_page.uv_cb.setChecked(bool(plan_raw.get("uv", True)))
        wizard.tools_page.vscode_cb.setChecked(bool(plan_raw.get("vscode", True)))
        wizard.tools_page.python_cb.setChecked(bool(plan_raw.get("python", True)))
        # Jump to progress and start immediately
        wizard.setStartId(wizard.pageIds()[3])
        wizard.show()
        return int(app.exec())

    mode = detect_mode_from_argv(args)
    wizard = InstallerWizard(mode)
    wizard.show()
    return int(app.exec())
```

</details>

## 🔧 Function `main`

```python
def main() -> None
```

CLI entry point for the installer wizard.

<details>
<summary>Code:</summary>

```python
def main() -> None:
    raise SystemExit(run_wizard())
```

</details>
