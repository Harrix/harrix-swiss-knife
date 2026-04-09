"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

import logging
import sys

import harrix_pylib as h
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

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
                    hsk.dev.OnUvUpdate,
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


def main() -> None:
    """Run the Harrix Swiss Knife application (tray icon and optional main window)."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    prune_action_output_dir()
    app: QApplication = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    output_bus = ActionOutputBus()
    main_menu: MainMenu = MainMenu(output_bus=output_bus)
    tray_icon: hsk.tray_icon.TrayIcon = hsk.tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu)
    tray_icon.setToolTip("Harrix Swiss Knife")
    tray_icon.show()

    config: dict = h.dev.config_load(get_config_path_str())
    show_main_window: bool = config.get("show_main_window_on_startup", True)

    main_window_instance: main_window.MainWindow = main_window.MainWindow(main_menu.menu, output_bus=output_bus)
    tray_icon.main_window = main_window_instance

    if show_main_window:
        main_window_instance.show_window()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
