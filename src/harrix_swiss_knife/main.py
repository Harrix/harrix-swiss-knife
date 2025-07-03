"""Main module for Harrix Swiss Knife application.

This module contains the main application logic for the Harrix Swiss Knife tool,
including the menu structure and application initialization.
"""

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import harrix_swiss_knife as hsk
from harrix_swiss_knife import resources_rc  # noqa: F401


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
                hsk.dev.OnGetMenu,
                hsk.dev.OnNpmInstallPackages,
                hsk.dev.OnNpmUpdatePackages,
                hsk.dev.OnOpenConfigJson,
                hsk.dev.OnUvUpdate,
            ],
        )

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_items(
            self.menu_images,
            [
                hsk.images.OnOptimize,
                hsk.images.OnOptimizeDialogReplace,
                hsk.images.OnOptimizeFile,
                hsk.images.OnResizeOptimizePngToAvif,
                hsk.images.OnOptimizeQuality,
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
                hsk.file.OnOpenCameraUploads,
                hsk.file.OnTreeViewFolder,
                hsk.file.OnTreeViewFolderIgnoreHiddenFolders,
                hsk.file.RenameLargestImagesToFeaturedImage,
            ],
        )

        # Menu Markdown
        self.menu_md = self.new_menu("Markdown", "📓")
        self.add_items(
            self.menu_md,
            [
                hsk.md.OnFormatQuotesAsMarkdownContent,
                hsk.md.OnGetListMoviesBooks,
                hsk.md.OnIncreaseHeadingLevelContent,
                "-",
                hsk.md.OnBeautifyMdNotesFolder,
                hsk.md.OnCheckMd,
                hsk.md.OnCheckMdFolder,
                hsk.md.OnCombineMarkdownFiles,
                hsk.md.OnDownloadAndReplaceImages,
                hsk.md.OnDownloadAndReplaceImagesFolder,
                hsk.md.OnFormatYaml,
                hsk.md.OnGenerateAuthorBook,
                hsk.md.OnGenerateImageCaptions,
                hsk.md.OnGenerateImageCaptionsFolder,
                hsk.md.OnGenerateShortNoteTocWithLinks,
                hsk.md.OnGenerateToc,
                hsk.md.OnGenerateTocFolder,
                hsk.md.OnOptimizeImages,
                hsk.md.OnOptimizeImagesFolder,
                hsk.md.OnOptimizeImagesFolderPngToAvif,
                hsk.md.OnPettierFolder,
                hsk.md.OnSortSections,
            ],
        )

        # New Markdown
        self.menu_new_md = self.new_menu("New Markdown", "𝐌")  # noqa: RUF001
        self.add_items(
            self.menu_new_md,
            [
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
                hsk.py.OnExtractFunctionsAndClasses,
                hsk.py.OnNewUvProject,
                hsk.py.OnNewUvProjectDialog,
                hsk.py.OnSortIsortFmtDocsPythonCodeFolder,
                hsk.py.OnSortIsortFmtPythonCodeFolder,
                "-",
                hsk.py.OnHarrixPylib02Publish,
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
                hsk.apps.OnFitness,
                "-",
                hsk.images.OnOptimizeClipboard,
                hsk.images.OnOptimizeClipboardDialog,
                "-",
                hsk.dev.OnExit,
            ],
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = hsk.tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu)
    tray_icon.setToolTip("harrix-swiss-knife")
    tray_icon.show()
    sys.exit(app.exec())
