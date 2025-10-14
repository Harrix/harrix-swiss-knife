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

        # Menu Dev
        self.menu_dev = self.new_menu("Dev", "🛠️")
        self.add_items(
            self.menu_dev,
            [
                hsk.dev.OnAboutDialog,
                hsk.dev.OnNpmManagePackages,
                hsk.dev.OnOpenConfigJson,
                hsk.dev.OnUvUpdate,
            ],
        )

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_items(
            self.menu_images,
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
        )

        # Menu File operations
        self.menu_file = self.new_menu("File operations", "🪟")
        self.add_items(
            self.menu_file,
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
        )

        # Menu Markdown
        self.menu_md = self.new_menu("Markdown", "📓")
        self.add_items(
            self.menu_md,
            [
                hsk.md.OnDecreaseHeadingLevelContent,
                hsk.md.OnGetListMoviesBooks,
                hsk.md.OnIncreaseHeadingLevelContent,
                hsk.md.OnQuotesProcess,
                "-",
                hsk.md.OnBeautifyMdFolder,
                hsk.md.OnBeautifyMdFolderAndRegenerateGMd,
                hsk.md.OnCheckMdFolder,
                hsk.md.OnDownloadAndReplaceImagesFolder,
                hsk.md.OnFixMarkdownWithQuotes,
                hsk.md.OnGenerateShortNoteTocWithLinks,
                hsk.md.OnOptimizeImagesFolder,
                hsk.md.OnOptimizeSelectedImages,
                hsk.md.OnSortSections,
            ],
        )

        # New Markdown
        self.menu_new_md = self.new_menu("New Markdown", "𝐌")  # noqa: RUF001
        self.add_items(
            self.menu_new_md,
            [
                hsk.md.OnAddMarkdownFromTemplate,
                "-",
                hsk.md.OnNewArticle,
                hsk.md.OnNewDiary,
                hsk.md.OnNewDiaryDream,
                hsk.md.OnNewNoteDialog,
                hsk.md.OnNewNoteDialogWithImages,
            ],
        )

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_items(
            self.menu_python,
            [
                hsk.py.OnCheckPythonFolder,
                hsk.py.OnNewUvLibrary,
                hsk.py.OnNewUvProject,
                hsk.py.OnPublishPythonLibrary,
                hsk.py.OnSortIsortFmtDocsPythonCodeFolder,
                hsk.py.OnSortIsortFmtPythonCodeFolder,
                hsk.py.OnUpdateUvDependencies,
            ],
        )

        # MainMenu
        self.add_menus_and_items(
            self.menu,
            menus=[
                self.menu_dev,
                self.menu_images,
                self.menu_file,
                self.menu_md,
                self.menu_new_md,
                self.menu_python,
            ],
            items=[
                hsk.apps.OnFinance,
                hsk.apps.OnFitness,
                hsk.apps.OnFood,
                "-",
                hsk.images.OnOptimizeClipboard,
                hsk.images.OnOptimizeClipboardDialog,
                "-",
                hsk.dev.OnExit,
            ],
        )


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
    config: dict = h.dev.load_config("config/config.json")
    show_main_window: bool = config.get("show_main_window_on_startup", True)

    # Create main window
    main_window_instance: main_window.MainWindow = main_window.MainWindow(main_menu.menu)
    tray_icon.main_window = main_window_instance

    # Show main window only if configured to do so
    if show_main_window:
        main_window_instance.show_window()

    # Run application event loop
    sys.exit(app.exec())
