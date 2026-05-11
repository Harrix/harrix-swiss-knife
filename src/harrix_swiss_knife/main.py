"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

import harrix_pylib as h
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

import harrix_swiss_knife as hsk
from harrix_swiss_knife import main_window, resources_rc  # noqa: F401
from harrix_swiss_knife.action_output_bus import ActionOutputBus
from harrix_swiss_knife.paths import get_config_path_str, prune_action_output_dir


class MainMenu(hsk.main_menu_base.MainMenuBase):
    """Main menu class that defines the application's menu structure.

    This class extends the MainMenuBase class and creates all the menu items
    and submenus for the application.
    """

    def __init__(self, *, output_bus: ActionOutputBus) -> None:
        """Initialize the main menu with all submenus and actions.

        Create and organizes all menu categories and their respective items.
        """
        super().__init__(output_bus=output_bus)

        # Define menu structure as a single array
        menu_structure = [
            (
                "Dev",
                "🛠️",
                [
                    hsk.dev.OnAboutDialog,
                    hsk.dev.OnDownloadOptimizeDependencies,
                    hsk.dev.OnNodeUpdate,
                    hsk.dev.OnNpmManagePackages,
                    hsk.dev.OnOpenConfigJson,
                    hsk.dev.OnViewRecentActionLogs,
                    hsk.dev.OnUvUpdate,
                    hsk.dev.OnSymlinkNotesExplorerExtension,
                ],
            ),
            (
                "Images",
                "🖼️",
                [
                    hsk.images.OnOpenPhotosInViewer,
                    "-",
                    hsk.images.OnOptimize,
                    hsk.images.OnOptimizeDialogReplace,
                    hsk.images.OnOptimizeQuality,
                    hsk.images.OnOptimizeResize,
                    hsk.images.OnOptimizeSingleImage,
                    "-",
                    hsk.images.OnClearImages,
                    hsk.images.OnOpenImages,
                    hsk.images.OnOpenOptimizedImages,
                ],
            ),
            (
                "File operations",
                "🪟",
                [
                    hsk.file.OnAllFilesToParentFolder,
                    hsk.file.OnBlockDisks,
                    hsk.file.OnCheckFeaturedImage,
                    hsk.file.OnCheckFeaturedImageInFolders,
                    hsk.file.OnExtractZipArchives,
                    hsk.file.OnCombineForAI,
                    hsk.file.OnListFilesSimple,
                    hsk.file.OnListFilesSimpleIgnoreHiddenFolders,
                    hsk.file.OnListFilesCurrentFolder,
                    hsk.file.OnRemoveEmptyFolders,
                    hsk.file.OnRenameFb2EpubPdfFiles,
                    hsk.file.OnRenameFilesByMapping,
                    hsk.file.OnRenameLastGitCommitWithEmoji,
                    hsk.file.OnRenameLargestImagesToFeaturedImage,
                    hsk.file.OnTreeViewFolder,
                    hsk.file.OnTreeViewFolderIgnoreHiddenFolders,
                ],
            ),
            (
                "Markdown",
                "📓",
                [
                    hsk.md.OnNewMarkdown,
                    "-",
                    hsk.md.OnDecreaseHeadingLevelContent,
                    hsk.md.OnGetListMoviesBooks,
                    hsk.md.OnIncreaseHeadingLevelContent,
                    "-",
                    hsk.md.OnAppendYamlTag,
                    hsk.md.OnBeautifyMdFolder,
                    hsk.md.OnBeautifyMdFolderAndRegenerateGMd,
                    hsk.md.OnCheckMdFolder,
                    hsk.md.OnDownloadAndReplaceImagesFolder,
                    hsk.md.OnFixMDWithQuotes,
                    hsk.md.OnGenerateShortNoteTocWithLinks,
                    hsk.md.OnGenerateStaticSite,
                    hsk.md.OnGetSetVariablesFromYaml,
                    hsk.md.OnOptimizeImagesFolder,
                    hsk.md.OnOptimizeSelectedImages,
                    hsk.md.OnSortSections,
                ],
            ),
            (
                "Python",
                "py.svg",
                [
                    hsk.py.OnCheckPythonFolder,
                    hsk.py.OnNewUvLibrary,
                    hsk.py.OnNewUvProject,
                    hsk.py.OnPublishPythonLibrary,
                    hsk.py.OnSortIsortFmtDocsPythonCodeFolder,
                    hsk.py.OnSortIsortFmtPythonCodeFolder,
                ],
            ),
            hsk.apps.OnFinance,
            hsk.apps.OnFitness,
            hsk.apps.OnFood,
            hsk.apps.OnHabits,
            "-",
            hsk.images.OnOptimizeClipboard,
            hsk.images.OnOptimizeClipboardDialog,
            "-",
            hsk.dev.OnExit,
        ]

        # Add all menus and items from structure
        self.add_menu_structure(self.menu, menu_structure)


def _get_log_dir() -> Path:
    """Pick a writable log directory: <repo>/logs first, then %LOCALAPPDATA%/harrix-swiss-knife/logs."""
    here = Path(__file__).resolve().parent  # src/harrix_swiss_knife
    project_root = here.parent.parent
    candidates = [project_root / "logs"]
    appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "harrix-swiss-knife" / "logs")
    candidates.append(Path.home() / ".harrix-swiss-knife" / "logs")
    for c in candidates:
        try:
            c.mkdir(parents=True, exist_ok=True)
            test = c / ".write-test"
            test.write_text("ok", encoding="utf-8")
            test.unlink(missing_ok=True)
        except Exception:
            logging.getLogger(__name__).debug("Log dir candidate is not writable: %s", c, exc_info=True)
        else:
            return c
    return Path.cwd()


def _log_environment(log: logging.Logger, log_path: Path) -> None:
    log.info("=" * 60)
    log.info("Starting Harrix Swiss Knife")
    log.info("Log file: %s", log_path)
    log.info("Python: %s", sys.version.replace("\n", " "))
    log.info("Platform: %s", sys.platform)
    log.info("Executable: %s", sys.executable)
    log.info("Argv: %s", sys.argv)
    log.info("CWD: %s", Path.cwd())


def _setup_file_logging() -> Path:
    """Add a rotating file handler so we can diagnose tray-not-appearing issues."""
    log_dir = _get_log_dir()
    log_path = log_dir / "main.log"
    root = logging.getLogger()
    if not any(isinstance(h_, RotatingFileHandler) for h_ in root.handlers):
        fh = RotatingFileHandler(str(log_path), maxBytes=2_000_000, backupCount=3, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        root.addHandler(fh)
    if root.level == logging.NOTSET or root.level > logging.INFO:
        root.setLevel(logging.INFO)
    return log_path


def _show_error_dialog(text: str) -> None:
    """Try to show a Qt error dialog when the app fails before reaching the tray."""
    try:
        if QApplication.instance() is None:
            QApplication(sys.argv)
        QMessageBox.critical(None, "Harrix Swiss Knife - Error", text)
    except Exception:
        logging.getLogger(__name__).debug("Failed to show Qt error dialog.", exc_info=True)


def main() -> None:
    """Run the Harrix Swiss Knife application (tray icon and optional main window)."""
    log_path = _setup_file_logging()
    log = logging.getLogger("harrix_swiss_knife")
    _log_environment(log, log_path)

    try:
        prune_action_output_dir()
        log.info("Creating QApplication")
        app: QApplication = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        app.setWindowIcon(QIcon(":/assets/logo.svg"))

        output_bus = ActionOutputBus()
        log.info("Building main menu")
        main_menu: MainMenu = MainMenu(output_bus=output_bus)
        log.info("Creating tray icon")
        tray_icon: hsk.tray_icon.TrayIcon = hsk.tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu)
        tray_icon.setToolTip("Harrix Swiss Knife")
        tray_icon.show()

        if not tray_icon.isSystemTrayAvailable():
            log.warning("System tray is not available on this system; tray icon will not be visible.")
        if not tray_icon.isVisible():
            log.warning("Tray icon failed to become visible. Windows may hide tray icons by default.")

        config: dict = h.dev.config_load(get_config_path_str())
        show_main_window: bool = config.get("show_main_window_on_startup", True)

        log.info("Creating main window (show_on_startup=%s)", show_main_window)
        main_window_instance: main_window.MainWindow = main_window.MainWindow(main_menu.menu, output_bus=output_bus)
        tray_icon.main_window = main_window_instance

        if show_main_window:
            main_window_instance.show_window()

        log.info("Entering Qt event loop")
        rc = app.exec()
        log.info("Qt event loop exited with code %s", rc)
        sys.exit(rc)
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log.exception("Fatal error during startup; exiting.")
        _show_error_dialog(f"Fatal error during startup.\n\nLog: {log_path}\n\n{tb}")
        sys.exit(1)


if __name__ == "__main__":
    main()
