import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import harrix_swiss_knife as hsk
from harrix_swiss_knife import resources_rc  # noqa
from harrix_swiss_knife import main_menu_base, tray_icon


class MainMenu(main_menu_base.MainMenuBase):
    def __init__(self):
        super().__init__()

        # Menu Dev
        self.menu_dev = self.new_menu("Dev", "🛠️")
        self.add_item(self.menu_dev, hsk.dev.OnGetMenu)
        self.add_item(self.menu_dev, hsk.dev.OnOpenConfigJson)
        self.add_item(self.menu_dev, hsk.dev.OnNpmInstallPackages)
        self.add_item(self.menu_dev, hsk.dev.OnNpmUpdatePackages)

        # Menu Apps
        self.menu_apps = self.new_menu("Apps", "💻")
        self.add_item(self.menu_apps, hsk.apps.OnFitness)

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, hsk.images.OnOptimize)
        self.add_item(self.menu_images, hsk.images.OnOptimizePngToAvif)
        self.add_item(self.menu_images, hsk.images.OnOptimizeQuality)
        self.add_item(self.menu_images, hsk.images.OnOptimizeDialogReplace)
        self.add_item(self.menu_images, hsk.images.OnOptimizeDialog)
        self.add_item(self.menu_images, hsk.images.OnOptimizeFile)
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, hsk.images.OnClearImages)
        self.add_item(self.menu_images, hsk.images.OnOpenImages)
        self.add_item(self.menu_images, hsk.images.OnOpenOptimizedImages)

        # Menu File operations
        self.menu_file = self.new_menu("File operations", "🪟")
        self.add_item(self.menu_file, hsk.file.OnAllFilesToParentFolder)
        self.add_item(self.menu_file, hsk.file.OnCheckFeaturedImage)
        self.add_item(self.menu_file, hsk.file.OnCheckFeaturedImageInFolders)
        self.add_item(self.menu_file, hsk.file.RenameLargestImagesToFeaturedImage)
        self.add_item(self.menu_file, hsk.file.OnBlockDisks)
        self.add_item(self.menu_file, hsk.file.OnOpenCameraUploads)
        self.add_item(self.menu_file, hsk.file.OnTreeViewFolderIgnoreHiddenFolders)
        self.add_item(self.menu_file, hsk.file.OnTreeViewFolder)

        # Menu Markdown
        self.menu_md = self.new_menu("Markdown", "📓")
        self.add_item(self.menu_md, hsk.md.OnNewDiaryDream)
        self.add_item(self.menu_md, hsk.md.OnNewDiary)
        self.add_item(self.menu_md, hsk.md.OnNewArticle)
        self.add_item(self.menu_md, hsk.md.OnNewNoteDialogWithImages)
        self.add_item(self.menu_md, hsk.md.OnNewNoteDialog)
        self.menu_md.addSeparator()
        self.add_item(self.menu_md, hsk.md.OnGetListMoviesBooks)
        self.add_item(self.menu_md, hsk.md.OnIncreaseHeadingLevelContent)
        self.menu_md.addSeparator()
        self.add_item(self.menu_md, hsk.md.OnBeautifyMdNotesAllInOne)
        self.menu_md.addSeparator()
        self.add_item(self.menu_md, hsk.md.OnDownloadAndReplaceImages)
        self.add_item(self.menu_md, hsk.md.OnDownloadAndReplaceImagesFolder)
        self.add_item(self.menu_md, hsk.md.OnFormatYaml)
        self.add_item(self.menu_md, hsk.md.OnGenerateAuthorBook)
        self.add_item(self.menu_md, hsk.md.OnGenerateImageCaptionsFolder)
        self.add_item(self.menu_md, hsk.md.OnGenerateImageCaptions)
        self.add_item(self.menu_md, hsk.md.OnGenerateTocFolder)
        self.add_item(self.menu_md, hsk.md.OnGenerateToc)
        self.add_item(self.menu_md, hsk.md.OnPettierFolder)
        self.add_item(self.menu_md, hsk.md.OnSortSectionsFolder)
        self.add_item(self.menu_md, hsk.md.OnSortSections)
        self.add_item(self.menu_md, hsk.md.OnCombineMarkdownFiles)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImages)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImagessFolder)

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, hsk.py.OnSortIsortFmtPythonCodeFolder)
        self.add_item(self.menu_python, hsk.py.OnNewUvProjectDialog)
        self.add_item(self.menu_python, hsk.py.OnNewUvProject)
        self.add_item(self.menu_python, hsk.py.OnSortCode)
        self.add_item(self.menu_python, hsk.py.OnSortCodeFolder)
        self.add_item(self.menu_python, hsk.py.OnExtractFunctionsAndClasses)
        self.add_item(self.menu_python, hsk.py.OnGenerateMdDocs)
        self.menu_python.addSeparator()
        self.add_item(self.menu_python, hsk.py.OnHarrixPylib01Prepare)
        self.add_item(self.menu_python, hsk.py.OnHarrixPylib02Publish)

        # MainMenu
        self.menu.addMenu(self.menu_dev)
        self.menu.addMenu(self.menu_apps)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_file)
        self.menu.addMenu(self.menu_md)
        self.menu.addMenu(self.menu_python)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.images.OnOptimizeClipboard)
        self.add_item(self.menu, hsk.images.OnOptimizeClipboardDialog)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.dev.OnExit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon(":/assets/logo.svg"))

    main_menu = MainMenu()

    tray_icon = tray_icon.TrayIcon(QIcon(":/assets/logo.svg"), menu=main_menu.menu, parent=app)
    tray_icon.setToolTip("harrix-swiss-knife")
    tray_icon.show()
    sys.exit(app.exec())
