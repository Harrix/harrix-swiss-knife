---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `main.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `MainMenu`](#%EF%B8%8F-class-mainmenu)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)

</details>

## 🏛️ Class `MainMenu`

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
```

</details>

### ⚙️ Method `__init__`

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
```

</details>
