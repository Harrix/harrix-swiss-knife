---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `menu_structure.py`

## 🔧 Function `get_menu_structure`

```python
def get_menu_structure() -> list[Any]
```

Return the tray menu structure as a nested list of submenus and action classes.

<details>
<summary>Code:</summary>

```python
def get_menu_structure() -> list[Any]:
    return [
        (
            "Dev",
            "🛠️",
            [
                OnAboutDialog,
                OnCreateDesktopShortcut,
                OnDownloadOptimizeDependencies,
                OnNodeUpdate,
                OnNpmManagePackages,
                OnOpenConfigJson,
                OnSyncQuickAccessToTotalCommander,
                OnUpdateHarrixSwissKnife,
                OnViewRecentActionLogs,
                OnClearTempFolder,
                OnUvUpdate,
                OnInstallCli,
                OnInstallHarrixNotesExplorerExtension,
            ],
        ),
        (
            "Images",
            "🖼️",
            [
                OnOpenPhotosInViewer,
                OnImageToMarkdownWithOcr,
                OnImageToMarkdownWithAI,
                "-",
                OnOptimize,
                OnOptimizeDialogReplace,
                OnOptimizeQuality,
                OnOptimizeResize,
                OnOptimizeSingleImage,
                "-",
                OnClearImages,
                OnOpenImages,
                OnOpenOptimizedImages,
                "-",
                OnOptimizeClipboard,
                OnOptimizeClipboardDialog,
            ],
        ),
        (
            "File operations",
            "🪟",
            [
                OnAllFilesToParentFolder,
                OnBlockDisks,
                OnCheckFeaturedImage,
                OnCheckFeaturedImageInFolders,
                OnExtractZipArchives,
                OnCombineForAI,
                OnConvertPathToWindows,
                OnListFilesSimple,
                OnListFilesSimpleIgnoreHiddenFolders,
                OnListFilesCurrentFolder,
                OnRemoveEmptyFolders,
                OnRenameDateInFilenames,
                OnRenameFb2EpubPdfFiles,
                OnRenameFilesByMapping,
                OnRenameLastGitCommitWithEmoji,
                OnRenameLargestImagesToFeaturedImage,
                OnTreeViewFolder,
                OnTreeViewFolderIgnoreHiddenFolders,
            ],
        ),
        (
            "Markdown",
            "📓",
            [
                OnNewMarkdown,
                "-",
                OnDecreaseHeadingLevelContent,
                OnGetListMoviesBooks,
                OnIncreaseHeadingLevelContent,
                "-",
                OnAppendYamlTag,
                OnBeautifyMdFolder,
                OnBeautifyMdFolderAndRegenerateGMd,
                OnCheckMdFolder,
                OnMoveMdIntoNamedFolders,
                OnDownloadAndReplaceImagesFolder,
                OnFixMDWithQuotes,
                OnGenerateShortNoteTocWithLinks,
                OnGenerateStaticSite,
                OnGetSetVariablesFromYaml,
                OnOptimizeImagesFolder,
                OnOptimizeSelectedImages,
                OnSortSections,
            ],
        ),
        (
            "Text",
            "✍️",
            [
                OnFixTextWithAI,
                OnRewriteTextWithAI,
                OnSpeechToTextWithAI,
                OnFixTextWithAIFromClipboard,
            ],
        ),
        (
            "Python",
            "py.svg",
            [
                OnCheckPythonFolder,
                OnCheckPythonProjects,
                OnNewUvLibrary,
                OnNewUvProject,
                OnPublishPythonLibrary,
                OnSortRuffFmtDocsPythonCodeFolder,
                OnSortRuffFmtPythonCodeFolder,
            ],
        ),
        OnFinance,
        OnFitness,
        OnFood,
        OnHabits,
        "-",
        OnQuickLauncher,
        "-",
        OnExit,
    ]
```

</details>
