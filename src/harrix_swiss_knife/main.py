"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

import logging
import sys
import traceback

import harrix_swiss_knife as hsk
from harrix_swiss_knife.action_output_bus import ActionOutputBus
from harrix_swiss_knife.app_startup import (
    log_startup_context,
    run_tray_application,
    setup_file_logging,
    show_fatal_error_dialog,
)


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
                    hsk.dev.OnCreateDesktopShortcut,
                    hsk.dev.OnDownloadOptimizeDependencies,
                    hsk.dev.OnNodeUpdate,
                    hsk.dev.OnNpmManagePackages,
                    hsk.dev.OnOpenConfigJson,
                    hsk.dev.OnUpdateHarrixSwissKnife,
                    hsk.dev.OnViewRecentActionLogs,
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
                    hsk.md.OnFixTextWithAI,
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
                    hsk.py.OnSortRuffFmtDocsPythonCodeFolder,
                    hsk.py.OnSortRuffFmtPythonCodeFolder,
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


def main() -> None:
    """Run the Harrix Swiss Knife application (tray icon and optional main window)."""
    log_path = setup_file_logging()
    log = logging.getLogger("harrix_swiss_knife")
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
