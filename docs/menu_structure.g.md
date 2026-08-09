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
                OnAddToAutostart,
                OnCreateDesktopShortcut,
                OnDownloadOptimizeDependencies,
                OnUpdateNode,
                OnNpmManagePackages,
                OnOpenConfigJson,
                OnSyncQuickAccessToTotalCommander,
                OnUpdateHarrixSwissKnife,
                OnViewRecentActionLogs,
                OnShowActionUsageStats,
                OnClearTempFolder,
                OnUpdateUv,
                OnInstallCli,
            ],
        ),
        (
            "Android",
            "📱",
            [
                OnAndroidFormat,
                OnAndroidCheck,
                OnAndroidBuild,
            ],
        ),
        (
            "VS Code",
            "💻",
            [
                OnVscodeFormat,
                OnVscodeCheck,
                OnSyncHarrixNotesExplorer,
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
                "-",
                OnScreenshotRegion,
            ],
        ),
        (
            "File operations",
            "🪟",
            [
                OnAllFilesToParentFolder,
                OnLockDisks,
                OnCheckFeaturedImage,
                OnCheckFeaturedImageInFolders,
                OnExtractZipArchives,
                OnCombineForAI,
                OnConvertPathToWindows,
                OnDiscardGitChanges,
                OnListFilesSimple,
                OnListFilesSimpleIgnoreHiddenFolders,
                OnListFilesCurrentFolder,
                OnRemoveEmptyFolders,
                OnRenameDateInFilenames,
                OnRenameFb2EpubPdfFiles,
                OnRenameFilesByMapping,
                OnGitCommitMessage,
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
                OnBeautifyMd,
                OnBeautifyMdAndRegenerateGMd,
                OnCheckMd,
                OnMoveMdIntoNamedFolders,
                OnDownloadAndReplaceImages,
                OnFixMdWithQuotes,
                OnGenerateShortNoteTocWithLinks,
                OnGenerateStaticSite,
                OnGetSetVariablesFromYaml,
                OnOptimizeImagesInMd,
                OnOptimizeSelectedImages,
                OnSortSections,
            ],
        ),
        (
            "Site",
            "🌐",
            [
                OnAddSiteContentSubmodule,
                OnFixSiteArticleLinkTitles,
                OnPullSiteSubmodules,
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
                OnHarrixCheckPython,
                OnCheckPythonProject,
                OnCheckPythonProjects,
                OnNewUvLibrary,
                OnNewUvProject,
                OnNewUvNotebook,
                OnPublishPythonLibrary,
                OnSortRuffFmtDocsPythonCode,
                OnSortRuffFmtPythonCode,
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
