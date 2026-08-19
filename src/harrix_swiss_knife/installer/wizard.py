"""PySide6 installer wizard."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from harrix_swiss_knife.installer.deploy import DeployOptions, pinned_python_version, run_deploy, suggest_install_root
from harrix_swiss_knife.installer.elevation import is_admin, read_plan_file, relaunch_elevated, write_plan_file
from harrix_swiss_knife.installer.log import OutcomeLog
from harrix_swiss_knife.installer.payload import extract_overlay, frozen_executable, is_frozen, read_overlay_bounds
from harrix_swiss_knife.installer.prereqs import PrerequisitePlan, default_plan_from_detection, detect_status

_SHELL_EXECUTE_MAX_ERROR = 32


class DonePage(QWizardPage):
    """Final wizard page shown after installation completes."""

    def __init__(self) -> None:
        """Build the completion page."""
        super().__init__()
        self.setTitle("Finished")
        self.label = QLabel("Installation finished. You can close this window.")
        self.label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)


class InstallerWizard(QWizard):
    """Main installer wizard coordinating all pages."""

    def __init__(self, mode: str) -> None:
        """Create wizard pages for the given install mode."""
        super().__init__()
        self.setWindowTitle(f"Harrix Swiss Knife — {'Offline' if mode == 'offline' else 'Online'} Installer")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(720, 520)
        self.mode = mode
        self.tools_page = ToolsPage(mode)
        self.options_page = OptionsPage()
        self.progress_page = ProgressPage(mode)
        self.addPage(WelcomePage(mode))
        self.addPage(self.tools_page)
        self.addPage(self.options_page)
        self.addPage(self.progress_page)
        self.addPage(DonePage())


class OptionsPage(QWizardPage):
    """Page for choosing install location and shortcuts."""

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


class ProgressPage(QWizardPage):
    """Page that runs deployment and shows live progress."""

    def __init__(self, mode: str) -> None:
        """Build the install progress UI."""
        super().__init__()
        self.setTitle("Installing")
        self._mode = mode
        self._worker: _Worker | None = None
        self._done = False
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas", 9))
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        layout = QVBoxLayout(self)
        layout.addWidget(self.bar)
        layout.addWidget(self.log_view)
        self.setCommitPage(True)
        self.setButtonText(QWizard.WizardButton.CommitButton, "Install")

    def isComplete(self) -> bool:  # noqa: N802
        """Return whether installation has finished."""
        return self._done

    def validatePage(self) -> bool:  # noqa: N802
        """Start installation or relaunch elevated when prerequisites require it."""
        if self._done:
            return True
        if self._worker is not None and self._worker.isRunning():
            return False
        wizard = self.wizard()
        assert isinstance(wizard, InstallerWizard)  # noqa: S101
        plan = wizard.tools_page.plan()
        if plan.need_elevate and not is_admin():
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
                return False
            # Elevated process continues; close this one.
            QApplication.instance().quit()  # type: ignore[union-attr]
            return False
        self._start_worker(plan)
        return False

    def _append(self, line: str) -> None:
        self.log_view.appendPlainText(line)

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

    def _start_worker(self, plan: PrerequisitePlan) -> None:
        wizard = self.wizard()
        assert isinstance(wizard, InstallerWizard)  # noqa: S101
        work = Path(tempfile.mkdtemp(prefix="hsk-install-"))
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
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


class ToolsPage(QWizardPage):
    """Page for selecting prerequisite tools to install."""

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


class WelcomePage(QWizardPage):
    """Introductory wizard page."""

    def __init__(self, mode: str) -> None:
        """Build the welcome text for the selected mode."""
        super().__init__()
        self.setTitle("Harrix Swiss Knife")
        label = QLabel(
            f"This wizard installs Harrix Swiss Knife "
            f"({'offline bundle' if mode == 'offline' else 'online from GitHub'}).\n\n"
            "You can choose which tools to install, the target folder, and shortcuts."
        )
        label.setWordWrap(True)
        layout = QVBoxLayout(self)
        layout.addWidget(label)


class _Worker(QThread):
    log_line = Signal(str)
    progress = Signal(int, int)
    finished_ok = Signal(object)
    finished_err = Signal(str)

    def __init__(
        self,
        *,
        mode: str,
        install_root: Path,
        plan: PrerequisitePlan,
        desktop: bool,
        startup: bool,
        work_dir: Path,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._mode = mode
        self._install_root = install_root
        self._plan = plan
        self._desktop = desktop
        self._startup = startup
        self._work_dir = work_dir

    def run(self) -> None:
        log = OutcomeLog()
        log_file = self._work_dir / "install.log"
        log.set_log(self.log_line.emit, log_file=log_file)
        try:
            exe = frozen_executable()
            deps: Path | None = None
            if is_frozen() and read_overlay_bounds(exe) is not None:
                payload_dir = self._work_dir / "payload"
                deps = extract_overlay(
                    exe,
                    payload_dir,
                    log=self.log_line.emit,
                    progress=self.progress.emit,
                )
            else:
                # Dev / unpackaged: use install/dependencies next to project
                here = Path(__file__).resolve()
                project = here.parents[3]
                candidate = project / "install" / "dependencies"
                if candidate.is_dir():
                    deps = candidate
                    self.log_line.emit(f"Using unpackaged dependencies: {deps}")
                else:
                    _raise_missing_dependencies_error()

            options = DeployOptions(
                mode=self._mode,
                install_root=self._install_root,
                plan=self._plan,
                desktop_shortcut=self._desktop,
                startup_shortcut=self._startup,
                deps_dir=deps,
                python_version=pinned_python_version(deps),
                allow_network=self._mode != "offline",
            )
            result = run_deploy(options, log)
            if result.ok:
                self.finished_ok.emit(result)
            else:
                self.finished_err.emit(result.error or "Deploy failed")
        except Exception as exc:
            self.finished_err.emit(str(exc))


def detect_mode_from_argv(argv: list[str]) -> str:
    """Detect online/offline mode from CLI flags or executable name."""
    if "--offline" in argv:
        return "offline"
    if "--online" in argv:
        return "online"
    exe = frozen_executable().name.lower()
    if "offline" in exe:
        return "offline"
    return "online"


def run_wizard(argv: list[str] | None = None) -> int:
    """Run the installer wizard and return the Qt exit code."""
    args = list(sys.argv[1:] if argv is None else argv)
    app = QApplication.instance() or QApplication(sys.argv)

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
        plan = PrerequisitePlan(
            git=bool(plan_raw.get("git", True)),
            uv=bool(plan_raw.get("uv", True)),
            vscode=bool(plan_raw.get("vscode", True)),
            python=bool(plan_raw.get("python", True)),
        )
        wizard.progress_page._start_worker(plan)  # noqa: SLF001
        return int(app.exec())

    mode = detect_mode_from_argv(args)
    wizard = InstallerWizard(mode)
    wizard.show()
    return int(app.exec())


def _raise_missing_dependencies_error() -> None:
    """Raise when neither payload overlay nor unpackaged dependencies exist."""
    msg = "No payload overlay and install/dependencies not found"
    raise RuntimeError(msg)


def main() -> None:
    """CLI entry point for the installer wizard."""
    raise SystemExit(run_wizard())
