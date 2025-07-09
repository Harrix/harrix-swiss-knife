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
        self.add_items(
            self.menu_dev,
            [
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
                hsk.md.OnGetListMoviesBooks,
                hsk.md.OnIncreaseHeadingLevelContent,
                hsk.md.OnQuotesFormatAsMarkdownContent,
                "-",
                hsk.md.OnBeautifyMdFolder,
                hsk.md.OnBeautifyMdFolderAndRegenerateGMd,
                hsk.md.OnCheckMdFolder,
                hsk.md.OnDownloadAndReplaceImages,
                hsk.md.OnDownloadAndReplaceImagesFolder,
                hsk.md.OnGenerateShortNoteTocWithLinks,
                hsk.md.OnOptimizeImages,
                hsk.md.OnOptimizeImagesFolder,
                hsk.md.OnOptimizeImagesFolderCompareSize,
                hsk.md.OnQuotesGenerateAuthorAndBook,
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
                hsk.py.OnNewUvProject,
                hsk.py.OnPublishPythonLibrary,
                hsk.py.OnSortIsortFmtDocsPythonCodeFolder,
                hsk.py.OnSortIsortFmtPythonCodeFolder,
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
        self.add_items(
            self.menu_dev,
            [
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
                hsk.md.OnGetListMoviesBooks,
                hsk.md.OnIncreaseHeadingLevelContent,
                hsk.md.OnQuotesFormatAsMarkdownContent,
                "-",
                hsk.md.OnBeautifyMdFolder,
                hsk.md.OnBeautifyMdFolderAndRegenerateGMd,
                hsk.md.OnCheckMdFolder,
                hsk.md.OnDownloadAndReplaceImages,
                hsk.md.OnDownloadAndReplaceImagesFolder,
                hsk.md.OnGenerateShortNoteTocWithLinks,
                hsk.md.OnOptimizeImages,
                hsk.md.OnOptimizeImagesFolder,
                hsk.md.OnOptimizeImagesFolderCompareSize,
                hsk.md.OnQuotesGenerateAuthorAndBook,
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
                hsk.py.OnNewUvProject,
                hsk.py.OnPublishPythonLibrary,
                hsk.py.OnSortIsortFmtDocsPythonCodeFolder,
                hsk.py.OnSortIsortFmtPythonCodeFolder,
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
```

</details>
