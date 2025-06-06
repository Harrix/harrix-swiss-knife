---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `main.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `MainMenu`](#class-mainmenu)
  - [Method `__init__`](#method-__init__)

</details>

## Class `MainMenu`

```python
class MainMenu(hsk.main_menu_base.MainMenuBase)
```

Main menu class that defines the application's menu structure.

This class extends the MainMenuBase class and creates all the menu items
and submenus for the application.

<details>
<summary>Code:</summary>

```python
class MainMenu(hsk.main_menu_base.MainMenuBase):

    def __init__(self) -> None:
        """Initialize the main menu with all submenus and actions.

        Create and organizes all menu categories and their respective items.
        """
        super().__init__()

        # Menu Dev
        self.menu_dev = self.new_menu("Dev", "🛠️")
        self.add_item(self.menu_dev, hsk.dev.OnGetMenu)
        self.add_item(self.menu_dev, hsk.dev.OnNpmInstallPackages)
        self.add_item(self.menu_dev, hsk.dev.OnNpmUpdatePackages)
        self.add_item(self.menu_dev, hsk.dev.OnOpenConfigJson)
        self.add_item(self.menu_dev, hsk.dev.OnUvUpdate)

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, hsk.images.OnOptimize)
        self.add_item(self.menu_images, hsk.images.OnOptimizeDialogReplace)
        self.add_item(self.menu_images, hsk.images.OnOptimizeFile)
        self.add_item(self.menu_images, hsk.images.OnOptimizePngToAvif)
        self.add_item(self.menu_images, hsk.images.OnOptimizeQuality)
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, hsk.images.OnClearImages)
        self.add_item(self.menu_images, hsk.images.OnOpenImages)
        self.add_item(self.menu_images, hsk.images.OnOpenOptimizedImages)

        # Menu File operations
        self.menu_file = self.new_menu("File operations", "🪟")
        self.add_item(self.menu_file, hsk.file.OnAllFilesToParentFolder)
        self.add_item(self.menu_file, hsk.file.OnBlockDisks)
        self.add_item(self.menu_file, hsk.file.OnCheckFeaturedImage)
        self.add_item(self.menu_file, hsk.file.OnCheckFeaturedImageInFolders)
        self.add_item(self.menu_file, hsk.file.OnOpenCameraUploads)
        self.add_item(self.menu_file, hsk.file.OnTreeViewFolder)
        self.add_item(self.menu_file, hsk.file.OnTreeViewFolderIgnoreHiddenFolders)
        self.add_item(self.menu_file, hsk.file.RenameLargestImagesToFeaturedImage)

        # Menu Markdown
        self.menu_md = self.new_menu("Markdown", "📓")
        self.add_item(self.menu_md, hsk.md.OnFormatQuotesAsMarkdownContent)
        self.add_item(self.menu_md, hsk.md.OnGetListMoviesBooks)
        self.add_item(self.menu_md, hsk.md.OnIncreaseHeadingLevelContent)
        self.menu_md.addSeparator()
        self.add_item(self.menu_md, hsk.md.OnCheckMd)
        self.add_item(self.menu_md, hsk.md.OnCheckMdFolder)
        self.add_item(self.menu_md, hsk.md.OnCombineMarkdownFiles)
        self.add_item(self.menu_md, hsk.md.OnDownloadAndReplaceImages)
        self.add_item(self.menu_md, hsk.md.OnDownloadAndReplaceImagesFolder)
        self.add_item(self.menu_md, hsk.md.OnFormatYaml)
        self.add_item(self.menu_md, hsk.md.OnGenerateAuthorBook)
        self.add_item(self.menu_md, hsk.md.OnGenerateImageCaptions)
        self.add_item(self.menu_md, hsk.md.OnGenerateImageCaptionsFolder)
        self.add_item(self.menu_md, hsk.md.OnGenerateShortNoteTocWithLinks)
        self.add_item(self.menu_md, hsk.md.OnGenerateToc)
        self.add_item(self.menu_md, hsk.md.OnGenerateTocFolder)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImages)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImagesFolder)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImagesFolderPngToAvif)
        self.add_item(self.menu_md, hsk.md.OnPettierFolder)
        self.add_item(self.menu_md, hsk.md.OnSortSections)

        # New Markdown
        self.menu_new_md = self.new_menu("New Markdown", "𝐌")  # noqa: RUF001
        self.add_item(self.menu_new_md, hsk.md.OnNewArticle)
        self.add_item(self.menu_new_md, hsk.md.OnNewDiary)
        self.add_item(self.menu_new_md, hsk.md.OnNewDiaryDream)
        self.add_item(self.menu_new_md, hsk.md.OnNewNoteDialog)
        self.add_item(self.menu_new_md, hsk.md.OnNewNoteDialogWithImages)

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, hsk.py.OnExtractFunctionsAndClasses)
        self.add_item(self.menu_python, hsk.py.OnNewUvProject)
        self.add_item(self.menu_python, hsk.py.OnNewUvProjectDialog)
        self.add_item(self.menu_python, hsk.py.OnSortIsortFmtPythonCodeFolder)
        self.add_item(self.menu_python, hsk.py.OnSortIsortFmtDocsPythonCodeFolder)
        self.menu_python.addSeparator()
        self.add_item(self.menu_python, hsk.py.OnHarrixPylib01Prepare)
        self.add_item(self.menu_python, hsk.py.OnHarrixPylib02Publish)

        # MainMenu
        self.menu.addMenu(self.menu_dev)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_file)
        self.menu.addMenu(self.menu_md)
        self.menu.addMenu(self.menu_new_md)
        self.menu.addMenu(self.menu_python)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.apps.OnFitness)
        self.add_item(self.menu, hsk.md.OnBeautifyMdNotesFolder)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.images.OnOptimizeClipboard)
        self.add_item(self.menu, hsk.images.OnOptimizeClipboardDialog)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.dev.OnExit)
```

</details>

### Method `__init__`

```python
def __init__(self) -> None
```

Initialize the main menu with all submenus and actions.

Create and organizes all menu categories and their respective items.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__()

        # Menu Dev
        self.menu_dev = self.new_menu("Dev", "🛠️")
        self.add_item(self.menu_dev, hsk.dev.OnGetMenu)
        self.add_item(self.menu_dev, hsk.dev.OnNpmInstallPackages)
        self.add_item(self.menu_dev, hsk.dev.OnNpmUpdatePackages)
        self.add_item(self.menu_dev, hsk.dev.OnOpenConfigJson)
        self.add_item(self.menu_dev, hsk.dev.OnUvUpdate)

        # Menu Images
        self.menu_images = self.new_menu("Images", "🖼️")
        self.add_item(self.menu_images, hsk.images.OnOptimize)
        self.add_item(self.menu_images, hsk.images.OnOptimizeDialogReplace)
        self.add_item(self.menu_images, hsk.images.OnOptimizeFile)
        self.add_item(self.menu_images, hsk.images.OnOptimizePngToAvif)
        self.add_item(self.menu_images, hsk.images.OnOptimizeQuality)
        self.menu_images.addSeparator()
        self.add_item(self.menu_images, hsk.images.OnClearImages)
        self.add_item(self.menu_images, hsk.images.OnOpenImages)
        self.add_item(self.menu_images, hsk.images.OnOpenOptimizedImages)

        # Menu File operations
        self.menu_file = self.new_menu("File operations", "🪟")
        self.add_item(self.menu_file, hsk.file.OnAllFilesToParentFolder)
        self.add_item(self.menu_file, hsk.file.OnBlockDisks)
        self.add_item(self.menu_file, hsk.file.OnCheckFeaturedImage)
        self.add_item(self.menu_file, hsk.file.OnCheckFeaturedImageInFolders)
        self.add_item(self.menu_file, hsk.file.OnOpenCameraUploads)
        self.add_item(self.menu_file, hsk.file.OnTreeViewFolder)
        self.add_item(self.menu_file, hsk.file.OnTreeViewFolderIgnoreHiddenFolders)
        self.add_item(self.menu_file, hsk.file.RenameLargestImagesToFeaturedImage)

        # Menu Markdown
        self.menu_md = self.new_menu("Markdown", "📓")
        self.add_item(self.menu_md, hsk.md.OnFormatQuotesAsMarkdownContent)
        self.add_item(self.menu_md, hsk.md.OnGetListMoviesBooks)
        self.add_item(self.menu_md, hsk.md.OnIncreaseHeadingLevelContent)
        self.menu_md.addSeparator()
        self.add_item(self.menu_md, hsk.md.OnCheckMd)
        self.add_item(self.menu_md, hsk.md.OnCheckMdFolder)
        self.add_item(self.menu_md, hsk.md.OnCombineMarkdownFiles)
        self.add_item(self.menu_md, hsk.md.OnDownloadAndReplaceImages)
        self.add_item(self.menu_md, hsk.md.OnDownloadAndReplaceImagesFolder)
        self.add_item(self.menu_md, hsk.md.OnFormatYaml)
        self.add_item(self.menu_md, hsk.md.OnGenerateAuthorBook)
        self.add_item(self.menu_md, hsk.md.OnGenerateImageCaptions)
        self.add_item(self.menu_md, hsk.md.OnGenerateImageCaptionsFolder)
        self.add_item(self.menu_md, hsk.md.OnGenerateShortNoteTocWithLinks)
        self.add_item(self.menu_md, hsk.md.OnGenerateToc)
        self.add_item(self.menu_md, hsk.md.OnGenerateTocFolder)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImages)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImagesFolder)
        self.add_item(self.menu_md, hsk.md.OnOptimizeImagesFolderPngToAvif)
        self.add_item(self.menu_md, hsk.md.OnPettierFolder)
        self.add_item(self.menu_md, hsk.md.OnSortSections)

        # New Markdown
        self.menu_new_md = self.new_menu("New Markdown", "𝐌")  # noqa: RUF001
        self.add_item(self.menu_new_md, hsk.md.OnNewArticle)
        self.add_item(self.menu_new_md, hsk.md.OnNewDiary)
        self.add_item(self.menu_new_md, hsk.md.OnNewDiaryDream)
        self.add_item(self.menu_new_md, hsk.md.OnNewNoteDialog)
        self.add_item(self.menu_new_md, hsk.md.OnNewNoteDialogWithImages)

        # Menu Python
        self.menu_python = self.new_menu("Python", "py.svg")
        self.add_item(self.menu_python, hsk.py.OnExtractFunctionsAndClasses)
        self.add_item(self.menu_python, hsk.py.OnNewUvProject)
        self.add_item(self.menu_python, hsk.py.OnNewUvProjectDialog)
        self.add_item(self.menu_python, hsk.py.OnSortIsortFmtPythonCodeFolder)
        self.add_item(self.menu_python, hsk.py.OnSortIsortFmtDocsPythonCodeFolder)
        self.menu_python.addSeparator()
        self.add_item(self.menu_python, hsk.py.OnHarrixPylib01Prepare)
        self.add_item(self.menu_python, hsk.py.OnHarrixPylib02Publish)

        # MainMenu
        self.menu.addMenu(self.menu_dev)
        self.menu.addMenu(self.menu_images)
        self.menu.addMenu(self.menu_file)
        self.menu.addMenu(self.menu_md)
        self.menu.addMenu(self.menu_new_md)
        self.menu.addMenu(self.menu_python)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.apps.OnFitness)
        self.add_item(self.menu, hsk.md.OnBeautifyMdNotesFolder)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.images.OnOptimizeClipboard)
        self.add_item(self.menu, hsk.images.OnOptimizeClipboardDialog)
        self.menu.addSeparator()
        self.add_item(self.menu, hsk.dev.OnExit)
```

</details>
