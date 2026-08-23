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
  - [⚙️ Method `set_report`](#%EF%B8%8F-method-set_report)
- [🏛️ Class `InstallerWizard`](#%EF%B8%8F-class-installerwizard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `accept`](#%EF%B8%8F-method-accept)
  - [⚙️ Method `is_install_running`](#%EF%B8%8F-method-is_install_running)
  - [⚙️ Method `reject`](#%EF%B8%8F-method-reject)
  - [⚙️ Method `show_install_report`](#%EF%B8%8F-method-show_install_report)
- [🏛️ Class `OptionsPage`](#%EF%B8%8F-class-optionspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `install_root`](#%EF%B8%8F-method-install_root)
  - [⚙️ Method `validatePage`](#%EF%B8%8F-method-validatepage)
- [🏛️ Class `ProgressPage`](#%EF%B8%8F-class-progresspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `initializePage`](#%EF%B8%8F-method-initializepage)
  - [⚙️ Method `isComplete`](#%EF%B8%8F-method-iscomplete)
  - [⚙️ Method `is_worker_running`](#%EF%B8%8F-method-is_worker_running)
  - [⚙️ Method `validatePage`](#%EF%B8%8F-method-validatepage-1)
- [🏛️ Class `ToolsPage`](#%EF%B8%8F-class-toolspage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `initializePage`](#%EF%B8%8F-method-initializepage-1)
  - [⚙️ Method `plan`](#%EF%B8%8F-method-plan)
  - [⚙️ Method `validatePage`](#%EF%B8%8F-method-validatepage-2)
- [🏛️ Class `UninstallWindow`](#%EF%B8%8F-class-uninstallwindow)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
- [🏛️ Class `WelcomePage`](#%EF%B8%8F-class-welcomepage)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
- [🔧 Function `append_log_line`](#-function-append_log_line)
- [🔧 Function `detect_mode_from_argv`](#-function-detect_mode_from_argv)
- [🔧 Function `load_app_icon`](#-function-load_app_icon)
- [🔧 Function `run_uninstall_wizard`](#-function-run_uninstall_wizard)
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
        """Build the completion page with a scrollable install report."""
        super().__init__()
        self.setTitle("Finished")
        self.label = QLabel("Installation finished. You can close this window.")
        self.label.setWordWrap(True)
        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setFont(QFont("Consolas", 9))
        self.report.setPlainText("Waiting for installation to finish…")
        copy_btn = QPushButton("Copy report")
        copy_btn.clicked.connect(self._copy_report)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.report)
        layout.addWidget(copy_btn)

    def set_report(self, text: str) -> None:
        """Show the install summary on this page."""
        self.report.setPlainText(text)

    def _copy_report(self) -> None:
        clip = QApplication.clipboard()
        if clip is not None:
            clip.setText(self.report.toPlainText())
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Build the completion page with a scrollable install report.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__()
        self.setTitle("Finished")
        self.label = QLabel("Installation finished. You can close this window.")
        self.label.setWordWrap(True)
        self.report = QPlainTextEdit()
        self.report.setReadOnly(True)
        self.report.setFont(QFont("Consolas", 9))
        self.report.setPlainText("Waiting for installation to finish…")
        copy_btn = QPushButton("Copy report")
        copy_btn.clicked.connect(self._copy_report)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.report)
        layout.addWidget(copy_btn)
```

</details>

### ⚙️ Method `set_report`

```python
def set_report(self, text: str) -> None
```

Show the install summary on this page.

<details>
<summary>Code:</summary>

```python
def set_report(self, text: str) -> None:
        self.report.setPlainText(text)
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
        self.done_page = DonePage()
        self.addPage(WelcomePage(mode))
        self.addPage(self.tools_page)
        self.addPage(self.options_page)
        self.addPage(self.progress_page)
        self.addPage(self.done_page)

    def accept(self) -> None:
        """Finish the wizard; confirm first if installation is still running."""
        if not self._confirm_abort_if_installing():
            return
        super().accept()

    def is_install_running(self) -> bool:
        """Return whether the install worker thread is still active."""
        return self.progress_page.is_worker_running()

    def reject(self) -> None:
        """Cancel/close the wizard; confirm first if installation is still running."""
        if not self._confirm_abort_if_installing():
            return
        super().reject()

    def show_install_report(self, result: DeployResult) -> None:
        """Populate the Finished page from a successful deploy result."""
        self.done_page.set_report(format_install_report(result))

    def _confirm_abort_if_installing(self) -> bool:
        """Return whether it is OK to close; ask when deploy is still running."""
        if not self.is_install_running():
            return True
        answer = QMessageBox.question(
            self,
            "Cancel installation?",
            "Installation is still in progress.\n\n"
            "If you cancel now, files that were already installed will remain on disk "
            "and must be removed manually.\n\n"
            "Are you sure you want to cancel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        return answer == QMessageBox.StandardButton.Yes
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
        self.done_page = DonePage()
        self.addPage(WelcomePage(mode))
        self.addPage(self.tools_page)
        self.addPage(self.options_page)
        self.addPage(self.progress_page)
        self.addPage(self.done_page)
```

</details>

### ⚙️ Method `accept`

```python
def accept(self) -> None
```

Finish the wizard; confirm first if installation is still running.

<details>
<summary>Code:</summary>

```python
def accept(self) -> None:
        if not self._confirm_abort_if_installing():
            return
        super().accept()
```

</details>

### ⚙️ Method `is_install_running`

```python
def is_install_running(self) -> bool
```

Return whether the install worker thread is still active.

<details>
<summary>Code:</summary>

```python
def is_install_running(self) -> bool:
        return self.progress_page.is_worker_running()
```

</details>

### ⚙️ Method `reject`

```python
def reject(self) -> None
```

Cancel/close the wizard; confirm first if installation is still running.

<details>
<summary>Code:</summary>

```python
def reject(self) -> None:
        if not self._confirm_abort_if_installing():
            return
        super().reject()
```

</details>

### ⚙️ Method `show_install_report`

```python
def show_install_report(self, result: DeployResult) -> None
```

Populate the Finished page from a successful deploy result.

<details>
<summary>Code:</summary>

```python
def show_install_report(self, result: DeployResult) -> None:
        self.done_page.set_report(format_install_report(result))
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
        self.hint = QLabel(
            "Recommended: `C:\\harrix-swiss-knife` (writable). "
            "`D:\\GitHub` / `C:\\GitHub` also work. "
            "Do not install under Program Files — the app needs to write into `.venv`."
        )
        self.hint.setWordWrap(True)
        self.desktop_cb = QCheckBox("Create desktop shortcut")
        self.desktop_cb.setChecked(True)
        self.startup_cb = QCheckBox("Add to Windows Startup")
        self.startup_cb.setChecked(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Install parent folder (repos will be cloned/extracted here):"))
        layout.addLayout(row)
        layout.addWidget(self.hint)
        layout.addWidget(self.desktop_cb)
        layout.addWidget(self.startup_cb)

    def install_root(self) -> Path:
        """Return the selected install parent folder."""
        return Path(self.path_edit.text().strip())

    def validatePage(self) -> bool:  # noqa: N802
        """Block folders so deep that `uv sync` could not write every packaged file."""
        root = self.install_root()
        if is_under_program_files(root):
            answer = QMessageBox.warning(
                self,
                "Program Files is not recommended",
                "Installing under Program Files usually breaks the tray app: "
                "`.venv` must stay writable for a normal (non-admin) user.\n\n"
                "Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
        headroom = venv_path_headroom(root)
        if headroom >= DEEPEST_VENV_RELATIVE or long_paths_enabled():
            return True
        answer = QMessageBox.question(
            self,
            "Folder path is too long",
            f"`{root}` leaves only {headroom} characters for files inside `.venv`, "
            f"but some packages need about {DEEPEST_VENV_RELATIVE}.\n\n"
            "Enable Windows long-path support now, or press No and pick a shorter folder "
            "such as `C:\\harrix-swiss-knife`.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        if enable_long_paths():
            return True
        QMessageBox.warning(
            self,
            "Long paths",
            "Could not enable long-path support (administrator rights are required). Please choose a shorter folder.",
        )
        return False

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
        self.hint = QLabel(
            "Recommended: `C:\\harrix-swiss-knife` (writable). "
            "`D:\\GitHub` / `C:\\GitHub` also work. "
            "Do not install under Program Files — the app needs to write into `.venv`."
        )
        self.hint.setWordWrap(True)
        self.desktop_cb = QCheckBox("Create desktop shortcut")
        self.desktop_cb.setChecked(True)
        self.startup_cb = QCheckBox("Add to Windows Startup")
        self.startup_cb.setChecked(True)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Install parent folder (repos will be cloned/extracted here):"))
        layout.addLayout(row)
        layout.addWidget(self.hint)
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

### ⚙️ Method `validatePage`

```python
def validatePage(self) -> bool
```

Block folders so deep that `uv sync` could not write every packaged file.

<details>
<summary>Code:</summary>

```python
def validatePage(self) -> bool:  # noqa: N802
        root = self.install_root()
        if is_under_program_files(root):
            answer = QMessageBox.warning(
                self,
                "Program Files is not recommended",
                "Installing under Program Files usually breaks the tray app: "
                "`.venv` must stay writable for a normal (non-admin) user.\n\n"
                "Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return False
        headroom = venv_path_headroom(root)
        if headroom >= DEEPEST_VENV_RELATIVE or long_paths_enabled():
            return True
        answer = QMessageBox.question(
            self,
            "Folder path is too long",
            f"`{root}` leaves only {headroom} characters for files inside `.venv`, "
            f"but some packages need about {DEEPEST_VENV_RELATIVE}.\n\n"
            "Enable Windows long-path support now, or press No and pick a shorter folder "
            "such as `C:\\harrix-swiss-knife`.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False
        if enable_long_paths():
            return True
        QMessageBox.warning(
            self,
            "Long paths",
            "Could not enable long-path support (administrator rights are required). Please choose a shorter folder.",
        )
        return False
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
        self._install_succeeded = False
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
        """Return whether installation has finished successfully."""
        return self._install_succeeded

    def is_worker_running(self) -> bool:
        """Return whether the background install thread is still active."""
        worker = self._worker
        return worker is not None and worker.isRunning()

    def validatePage(self) -> bool:  # noqa: N802
        """Allow leaving the page only after a successful install; Retry restarts on failure."""
        if self._install_succeeded:
            return True
        if self.is_worker_running():
            return False
        self._retry_install()
        return False

    def _append(self, line: str) -> None:
        append_log_line(self.log_view, line)
        self._update_status_from_log(line)

    def _begin_if_needed(self) -> None:
        if self._install_succeeded:
            return
        if self.is_worker_running():
            return
        if self._worker is not None:
            self._worker = None
        wizard = self.wizard()
        if not isinstance(wizard, InstallerWizard):
            return
        plan = wizard.tools_page.plan()
        if plan.need_elevate and not is_admin():
            self._append("⚠️ Running without administrator rights; Git or VS Code setup may fail.")
        self._start_worker(plan)

    def _on_err(self, message: str) -> None:
        self._append(f"❌ {message}")
        self._worker = None
        self.completeChanged.emit()
        QMessageBox.critical(self, "Install failed", message)
        wizard = self.wizard()
        if wizard:
            wizard.button(QWizard.WizardButton.BackButton).setEnabled(True)
            wizard.button(QWizard.WizardButton.CommitButton).setEnabled(True)
            self.setButtonText(QWizard.WizardButton.CommitButton, "Retry")

    def _on_ok(self, result: object) -> None:
        self._install_succeeded = True
        self.bar.setRange(0, 1)
        self.bar.setValue(1)
        self.completeChanged.emit()
        wizard = self.wizard()
        if isinstance(wizard, InstallerWizard) and isinstance(result, DeployResult):
            wizard.show_install_report(result)
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

    def _retry_install(self) -> None:
        """Start installation again after a failed run (Commit / Retry button)."""
        wizard = self.wizard()
        if not isinstance(wizard, InstallerWizard):
            return
        if self.is_worker_running():
            return
        self._worker = None
        self.setButtonText(QWizard.WizardButton.CommitButton, "Install")
        self._append("==> Retrying installation")
        plan = wizard.tools_page.plan()
        if plan.need_elevate and not is_admin():
            self._append("⚠️ Running without administrator rights; Git or VS Code setup may fail.")
        self._start_worker(plan)

    def _start_worker(self, plan: PrerequisitePlan) -> None:
        wizard = self.wizard()
        assert isinstance(wizard, InstallerWizard)  # noqa: S101
        work = create_work_dir()
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
        if not text:
            return
        mode = progress_mode_for_log_line(line, extracting=self._extracting)
        if mode is ProgressBarMode.INDETERMINATE:
            self._extracting = False
            self.bar.setRange(0, 0)
        elif mode is ProgressBarMode.DETERMINATE:
            self._extracting = True
        if text.startswith("==> "):
            self._extracting = "extract" in text.lower()
            if not self._extracting:
                self.bar.setRange(0, 0)
            self.status_label.setText(text[4:])
            return
        if text.startswith("Extracting payload"):
            self._extracting = True
            self.status_label.setText("Extracting installer payload")
            self.detail_label.setText(text)
            return
        if line.startswith("  ") or text[:1] in {"✅", "⚠️", "❌", "i", "•"}:
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
        self._install_succeeded = False
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

Return whether installation has finished successfully.

<details>
<summary>Code:</summary>

```python
def isComplete(self) -> bool:  # noqa: N802
        return self._install_succeeded
```

</details>

### ⚙️ Method `is_worker_running`

```python
def is_worker_running(self) -> bool
```

Return whether the background install thread is still active.

<details>
<summary>Code:</summary>

```python
def is_worker_running(self) -> bool:
        worker = self._worker
        return worker is not None and worker.isRunning()
```

</details>

### ⚙️ Method `validatePage`

```python
def validatePage(self) -> bool
```

Allow leaving the page only after a successful install; Retry restarts on failure.

<details>
<summary>Code:</summary>

```python
def validatePage(self) -> bool:  # noqa: N802
        if self._install_succeeded:
            return True
        if self.is_worker_running():
            return False
        self._retry_install()
        return False
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
        self.python_ext_cb = QCheckBox("Install Python extension (VS Code / Cursor)")
        self._status: DetectionStatus | None = None
        self._reinstall_confirmed: frozenset[str] = frozenset()
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.git_cb)
        layout.addWidget(self.uv_cb)
        layout.addWidget(self.vscode_cb)
        layout.addWidget(self.python_cb)
        layout.addWidget(self.python_ext_cb)

    def initializePage(self) -> None:  # noqa: N802
        """Populate tool checkboxes from detected system status."""
        status = detect_status()
        self._status = status
        self._reinstall_confirmed = frozenset()
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
        self.python_ext_cb.setChecked(plan.python_extension)

    def plan(self) -> PrerequisitePlan:
        """Return the user's selected prerequisite install plan."""
        return PrerequisitePlan(
            git=self.git_cb.isChecked(),
            uv=self.uv_cb.isChecked(),
            vscode=self.vscode_cb.isChecked(),
            python=self.python_cb.isChecked(),
            python_extension=self.python_ext_cb.isChecked(),
            reinstall_confirmed=self._reinstall_confirmed,
        )

    def validatePage(self) -> bool:  # noqa: N802
        """Confirm reinstall when the user re-selects tools already on this PC."""
        if self._status is None:
            return True
        plan = self.plan()
        keys = detected_reinstall_keys(plan, self._status)
        if not keys:
            self._reinstall_confirmed = frozenset()
            return True
        answer = QMessageBox.question(
            self,
            "Reinstall selected tools?",
            format_reinstall_warning(keys),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            checkbox_by_key = {
                "git": self.git_cb,
                "uv": self.uv_cb,
                "vscode": self.vscode_cb,
                "python": self.python_cb,
            }
            for key in keys:
                checkbox = checkbox_by_key.get(key)
                if checkbox is not None:
                    checkbox.setChecked(False)
            self._reinstall_confirmed = frozenset()
            QMessageBox.information(
                self,
                "Install skipped for existing tools",
                "Unchecked tools that are already installed. You can continue with the remaining selections.",
            )
            return False
        self._reinstall_confirmed = frozenset(keys)
        return True
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
        self.python_ext_cb = QCheckBox("Install Python extension (VS Code / Cursor)")
        self._status: DetectionStatus | None = None
        self._reinstall_confirmed: frozenset[str] = frozenset()
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addWidget(self.git_cb)
        layout.addWidget(self.uv_cb)
        layout.addWidget(self.vscode_cb)
        layout.addWidget(self.python_cb)
        layout.addWidget(self.python_ext_cb)
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
        self._status = status
        self._reinstall_confirmed = frozenset()
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
        self.python_ext_cb.setChecked(plan.python_extension)
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
            python_extension=self.python_ext_cb.isChecked(),
            reinstall_confirmed=self._reinstall_confirmed,
        )
```

</details>

### ⚙️ Method `validatePage`

```python
def validatePage(self) -> bool
```

Confirm reinstall when the user re-selects tools already on this PC.

<details>
<summary>Code:</summary>

```python
def validatePage(self) -> bool:  # noqa: N802
        if self._status is None:
            return True
        plan = self.plan()
        keys = detected_reinstall_keys(plan, self._status)
        if not keys:
            self._reinstall_confirmed = frozenset()
            return True
        answer = QMessageBox.question(
            self,
            "Reinstall selected tools?",
            format_reinstall_warning(keys),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            checkbox_by_key = {
                "git": self.git_cb,
                "uv": self.uv_cb,
                "vscode": self.vscode_cb,
                "python": self.python_cb,
            }
            for key in keys:
                checkbox = checkbox_by_key.get(key)
                if checkbox is not None:
                    checkbox.setChecked(False)
            self._reinstall_confirmed = frozenset()
            QMessageBox.information(
                self,
                "Install skipped for existing tools",
                "Unchecked tools that are already installed. You can continue with the remaining selections.",
            )
            return False
        self._reinstall_confirmed = frozenset(keys)
        return True
```

</details>

## 🏛️ Class `UninstallWindow`

```python
class UninstallWindow(QWidget)
```

Simple uninstall UI: confirm path, show preserved data, run removal.

<details>
<summary>Code:</summary>

```python
class UninstallWindow(QWidget):

    def __init__(self, hsk_path: Path) -> None:
        """Build the uninstall form for `hsk_path`."""
        super().__init__()
        self.setWindowTitle("Uninstall Harrix Swiss Knife")
        self.setMinimumSize(640, 480)
        icon = load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self._worker: _UninstallWorker | None = None
        self._done = False

        self.path_edit = QLineEdit(str(hsk_path))
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse)

        self.siblings_cb = QCheckBox("Also remove sibling repos harrix-pylib and harrix-pyssg")
        self.siblings_cb.setChecked(True)

        preserve = default_preserve_dir(hsk_path)
        self.info = QLabel(
            "This removes the app folders, desktop/startup shortcuts, and the global `hsk` CLI.\n"
            "Git, uv, VS Code, and Python are left installed.\n\n"
            f"Databases, api-keys, and fitness images are moved to:\n{preserve}"
        )
        self.info.setWordWrap(True)

        self.preserve_list = QPlainTextEdit()
        self.preserve_list.setReadOnly(True)
        self.preserve_list.setMaximumHeight(120)
        self._refresh_preserve_list()

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.bar = QProgressBar()
        self.bar.setRange(0, 1)
        self.bar.setValue(0)

        self.start_btn = QPushButton("Uninstall")
        self.start_btn.clicked.connect(self._start)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.start_btn)
        buttons.addWidget(self.close_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Install folder (harrix-swiss-knife):"))
        layout.addLayout(path_row)
        layout.addWidget(self.siblings_cb)
        layout.addWidget(self.info)
        layout.addWidget(QLabel("Items that will be preserved:"))
        layout.addWidget(self.preserve_list)
        layout.addWidget(self.bar)
        layout.addWidget(self.log_view)
        layout.addLayout(buttons)
        self.path_edit.textChanged.connect(self._refresh_preserve_list)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select harrix-swiss-knife folder", self.path_edit.text())
        if path:
            self.path_edit.setText(path)

    def _on_err(self, message: str) -> None:
        self._done = True
        self.bar.setRange(0, 1)
        self.bar.setValue(0)
        self.start_btn.setEnabled(True)
        QMessageBox.critical(self, "Uninstall failed", message)

    def _on_ok(self, result: object) -> None:
        self._done = True
        self.bar.setRange(0, 1)
        self.bar.setValue(1)
        if isinstance(result, UninstallResult):
            report = format_uninstall_report(result)
            append_log_line(self.log_view, report)
            QMessageBox.information(self, "Uninstall finished", report[:1500])
        else:
            preserved = getattr(result, "preserved_dir", None)
            msg = "Uninstall finished."
            if preserved is not None:
                msg += f"\n\nPreserved data:\n{preserved}"
            QMessageBox.information(self, "Uninstall finished", msg)

    def _refresh_preserve_list(self) -> None:
        hsk = Path(self.path_edit.text().strip())
        if not hsk.is_dir():
            self.preserve_list.setPlainText("(folder not found)")
            return
        items = list_paths_to_preserve(hsk)
        if not items:
            self.preserve_list.setPlainText("(no databases or api-keys under this folder)")
            return
        root = hsk.resolve()
        lines = []
        for path in items:
            try:
                lines.append(str(path.relative_to(root)))
            except ValueError:
                lines.append(str(path))
        self.preserve_list.setPlainText("\n".join(lines))
        preserve = default_preserve_dir(hsk)
        self.info.setText(
            "This removes the app folders, desktop/startup shortcuts, and the global `hsk` CLI.\n"
            "Git, uv, VS Code, and Python are left installed.\n\n"
            f"Databases, api-keys, and fitness images are moved to:\n{preserve}"
        )

    def _start(self) -> None:
        if self._done or self._worker is not None:
            return
        hsk = Path(self.path_edit.text().strip())
        answer = QMessageBox.question(
            self,
            "Confirm uninstall",
            f"Uninstall Harrix Swiss Knife from:\n{hsk}\n\nDatabases will be kept.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.start_btn.setEnabled(False)
        self.bar.setRange(0, 0)
        self._worker = _UninstallWorker(
            hsk_path=hsk,
            remove_siblings=self.siblings_cb.isChecked(),
            parent=self,
        )
        self._worker.log_line.connect(lambda line: append_log_line(self.log_view, line))
        self._worker.finished_ok.connect(self._on_ok)
        self._worker.finished_err.connect(self._on_err)
        self._worker.start()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, hsk_path: Path) -> None
```

Build the uninstall form for `hsk_path`.

<details>
<summary>Code:</summary>

```python
def __init__(self, hsk_path: Path) -> None:
        super().__init__()
        self.setWindowTitle("Uninstall Harrix Swiss Knife")
        self.setMinimumSize(640, 480)
        icon = load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self._worker: _UninstallWorker | None = None
        self._done = False

        self.path_edit = QLineEdit(str(hsk_path))
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse)

        self.siblings_cb = QCheckBox("Also remove sibling repos harrix-pylib and harrix-pyssg")
        self.siblings_cb.setChecked(True)

        preserve = default_preserve_dir(hsk_path)
        self.info = QLabel(
            "This removes the app folders, desktop/startup shortcuts, and the global `hsk` CLI.\n"
            "Git, uv, VS Code, and Python are left installed.\n\n"
            f"Databases, api-keys, and fitness images are moved to:\n{preserve}"
        )
        self.info.setWordWrap(True)

        self.preserve_list = QPlainTextEdit()
        self.preserve_list.setReadOnly(True)
        self.preserve_list.setMaximumHeight(120)
        self._refresh_preserve_list()

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.bar = QProgressBar()
        self.bar.setRange(0, 1)
        self.bar.setValue(0)

        self.start_btn = QPushButton("Uninstall")
        self.start_btn.clicked.connect(self._start)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.start_btn)
        buttons.addWidget(self.close_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Install folder (harrix-swiss-knife):"))
        layout.addLayout(path_row)
        layout.addWidget(self.siblings_cb)
        layout.addWidget(self.info)
        layout.addWidget(QLabel("Items that will be preserved:"))
        layout.addWidget(self.preserve_list)
        layout.addWidget(self.bar)
        layout.addWidget(self.log_view)
        layout.addLayout(buttons)
        self.path_edit.textChanged.connect(self._refresh_preserve_list)
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

## 🔧 Function `append_log_line`

```python
def append_log_line(view: QPlainTextEdit, line: str) -> None
```

Append a log line and scroll the view to the newest text.

<details>
<summary>Code:</summary>

```python
def append_log_line(view: QPlainTextEdit, line: str) -> None:
    view.appendPlainText(line)

    def _scroll_to_end() -> None:
        bar = view.verticalScrollBar()
        bar.setValue(bar.maximum())

    # Layout updates after append; scroll on the next event-loop tick.
    QTimer.singleShot(0, _scroll_to_end)
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

## 🔧 Function `run_uninstall_wizard`

```python
def run_uninstall_wizard(argv: list[str] | None = None) -> int
```

Run the uninstall UI (or silent uninstall) and return the process exit code.

<details>
<summary>Code:</summary>

```python
def run_uninstall_wizard(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    silent = "--silent" in raw
    args = [a for a in raw if a not in {"--uninstall", "--silent"}]
    hint: Path | None = None
    for arg in args:
        if arg.startswith("-"):
            continue
        candidate = Path(arg)
        if candidate.is_dir():
            hint = candidate
            break
    hsk = detect_hsk_path(hint)

    if silent:
        if hsk is None:
            print("Could not find harrix-swiss-knife install folder", file=sys.stderr)
            return 1
        if sys.platform == "win32" and not is_admin() and "--no-elevate" not in raw:
            try:
                rc = relaunch_elevated(["--uninstall", "--silent", str(hsk)])
            except (OSError, RuntimeError):
                rc = 0
            if rc > _SHELL_EXECUTE_MAX_ERROR:
                return 0
        log = OutcomeLog()
        result = run_uninstall(
            UninstallOptions(hsk_path=hsk, remove_sibling_repos=True),
            log,
        )
        print(format_uninstall_report(result))
        return 0 if result.ok else 1

    if sys.platform == "win32" and not is_admin() and "--no-elevate" not in raw:
        elevate_args = ["--uninstall"]
        if hsk is not None:
            elevate_args.append(str(hsk))
        try:
            rc = relaunch_elevated(elevate_args)
        except (OSError, RuntimeError):
            rc = 0
        if rc > _SHELL_EXECUTE_MAX_ERROR:
            return 0

    app = QApplication.instance() or QApplication(sys.argv)
    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    if hsk is None:
        QMessageBox.critical(
            None,
            "Uninstall",
            "Could not find a harrix-swiss-knife install folder.\nPass the folder path as an argument or browse to it.",
        )
        # Still show UI with empty/default path for browsing.
        hsk = Path.home() / "harrix-swiss-knife" / "harrix-swiss-knife"
    window = UninstallWindow(hsk)
    window.show()
    return int(app.exec())
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
    if "--uninstall" in args:
        return run_uninstall_wizard(args)
    if _elevate_before_ui(args):
        return 0
    app = QApplication.instance() or QApplication(sys.argv)
    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)

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
