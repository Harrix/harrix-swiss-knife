"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

import sys

import harrix_pylib as h
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import harrix_swiss_knife as hsk
from harrix_swiss_knife import main_window, resources_rc  # noqa: F401


class MainMenu(hsk.main_menu_base.MainMenuBase):
    """Main menu class that defines the application's menu structure.

    This class extends the MainMenuBase class and creates all the menu items
    and submenus for the application.
    """

    def __init__(self) -> None:
        """Initialize the main menu with all submenus and actions.

        Create and organizes all menu categories and their respective items.
        """
        super().__init__()

        # Define menu structure as a single array
        menu_structure = [
            (
                "Dev",
                "🛠️",
                [
                    hsk.dev.OnAboutDialog,
                    hsk.dev.OnNpmManagePackages,
                    hsk.dev.OnOpenConfigJson,
                    hsk.dev.OnUvUpdate,
                ],
            ),
            (
                "Images",
                "🖼️",
                [
                    hsk.images.OnOpenCameraUploads,
                    hsk.images.OnOpenCameraUploadsShort,
                    "-",
                    hsk.images.OnOptimize,
                    hsk.images.OnOptimizeDialogReplace,
                    hsk.images.OnOptimizeQuality,
                    hsk.images.OnOptimizeResizePngToAvif,
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
                    hsk.md.OnDecreaseHeadingLevelContent,
                    hsk.md.OnGetListMoviesBooks,
                    hsk.md.OnIncreaseHeadingLevelContent,
                    "-",
                    hsk.md.OnBeautifyMdFolder,
                    hsk.md.OnBeautifyMdFolderAndRegenerateGMd,
                    hsk.md.OnCheckMdFolder,
                    hsk.md.OnDownloadAndReplaceImagesFolder,
                    hsk.md.OnFixMDWithQuotes,
                    hsk.md.OnGenerateShortNoteTocWithLinks,
                    hsk.md.OnGenerateStaticSite,
                    hsk.md.OnOptimizeImagesFolder,
                    hsk.md.OnOptimizeSelectedImages,
                    hsk.md.OnSortSections,
                    hsk.md.OnAppendYamlTag,
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
            "-",
            hsk.md.OnNewMarkdown,
            "-",
            hsk.images.OnOptimizeClipboard,
            hsk.images.OnOptimizeClipboardDialog,
            "-",
            hsk.dev.OnExit,
        ]

        # Add all menus and items from structure
        self.add_menu_structure(self.menu, menu_structure)


if __name__ == "__main__":
    # Initialize Qt application
    app: QApplication = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    # Create main menu
    main_menu: MainMenu = MainMenu()

    # Create and configure system tray icon
    tray_icon: hsk.tray_icon.TrayIcon = hsk.tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu)
    tray_icon.setToolTip("Harrix Swiss Knife")
    tray_icon.show()

    # Load configuration
    config: dict = h.dev.config_load("config/config.json")
    show_main_window: bool = config.get("show_main_window_on_startup", True)

    # Create main window
    main_window_instance: main_window.MainWindow = main_window.MainWindow(main_menu.menu)
    tray_icon.main_window = main_window_instance

    # Show main window only if configured to do so
    if show_main_window:
        main_window_instance.show_window()

    # Run application event loop
    sys.exit(app.exec())
