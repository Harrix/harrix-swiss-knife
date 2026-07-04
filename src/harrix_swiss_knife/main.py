"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

from __future__ import annotations

import logging
import sys
import traceback
from typing import Any

import harrix_swiss_knife as hsk
from harrix_swiss_knife.action_output_bus import ActionOutputBus
from harrix_swiss_knife.app_startup import (
    install_diagnostic_handlers,
    log_startup_context,
    run_tray_application,
    setup_file_logging,
    show_fatal_error_dialog,
)


def get_menu_structure() -> list[Any]:
    """Return the tray menu structure as a nested list of submenus and action classes."""
    return [
        (
            "Dev",
            "🛠️",
            [
                hsk.dev.OnAboutDialog,
                hsk.dev.OnCreateDesktopShortcut,
                hsk.dev.OnDownloadOptimizeDependencies,
                hsk.dev.OnNodeUpdate,
                hsk.dev.OnNpmManagePackages,
                hsk.dev.OnOpenConfigJson,
                hsk.dev.OnUpdateHarrixSwissKnife,
                hsk.dev.OnViewRecentActionLogs,
                hsk.dev.OnClearTempFolder,
                hsk.dev.OnUvUpdate,
                hsk.dev.OnInstallHarrixNotesExplorerExtension,
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
                "-",
                hsk.images.OnOptimizeClipboard,
                hsk.images.OnOptimizeClipboardDialog,
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
                hsk.file.OnRenameDateInFilenames,
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
                hsk.md.OnMoveMdIntoNamedFolders,
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
            "Text",
            "✍️",
            [
                hsk.text.OnFixTextWithAI,
                hsk.text.OnFixSpeechWithAI,
                hsk.text.OnFixTextWithAIFromClipboard,
            ],
        ),
        (
            "Python",
            "py.svg",
            [
                hsk.py.OnCheckPythonFolder,
                hsk.py.OnCheckPythonProjects,
                hsk.py.OnNewUvLibrary,
                hsk.py.OnNewUvProject,
                hsk.py.OnPublishPythonLibrary,
                hsk.py.OnSortRuffFmtDocsPythonCodeFolder,
                hsk.py.OnSortRuffFmtPythonCodeFolder,
            ],
        ),
        hsk.app_actions.OnFinance,
        hsk.app_actions.OnFitness,
        hsk.app_actions.OnFood,
        hsk.app_actions.OnHabits,
        "-",
        hsk.text.OnQuickLauncher,
        "-",
        hsk.dev.OnExit,
    ]


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
        self.add_menu_structure(self.menu, get_menu_structure())


def main() -> None:
    """Run the Harrix Swiss Knife application (tray icon and optional main window)."""
    log_path = setup_file_logging()
    log = logging.getLogger("harrix_swiss_knife")
    install_diagnostic_handlers(log)
    log_startup_context(log, log_path)

    try:
        rc = run_tray_application(log, main_menu_cls=MainMenu)
        sys.exit(rc)
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log.exception("Fatal error during startup; exiting.")
        show_fatal_error_dialog(f"Fatal error during startup.\n\nLog: {log_path}\n\n{tb}")
        sys.exit(1)


if __name__ == "__main__":
    main()
