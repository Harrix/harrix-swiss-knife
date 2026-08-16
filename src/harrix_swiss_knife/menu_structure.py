"""Tray menu structure shared by MainMenu and quick launcher registry."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.android.android_build import OnAndroidBuild
from harrix_swiss_knife.actions.android.android_check import OnAndroidCheck
from harrix_swiss_knife.actions.android.android_format import OnAndroidFormat
from harrix_swiss_knife.actions.apps.finance import OnFinance
from harrix_swiss_knife.actions.apps.fitness import OnFitness
from harrix_swiss_knife.actions.apps.food import OnFood
from harrix_swiss_knife.actions.apps.habits import OnHabits
from harrix_swiss_knife.actions.apps.icons import OnIcons
from harrix_swiss_knife.actions.development.about_dialog import OnAboutDialog
from harrix_swiss_knife.actions.development.add_to_autostart import OnAddToAutostart
from harrix_swiss_knife.actions.development.clear_temp_folder import OnClearTempFolder
from harrix_swiss_knife.actions.development.create_desktop_shortcut import OnCreateDesktopShortcut
from harrix_swiss_knife.actions.development.download_optimize_dependencies import OnDownloadOptimizeDependencies
from harrix_swiss_knife.actions.development.exit_ import OnExit
from harrix_swiss_knife.actions.development.install_cli import OnInstallCli
from harrix_swiss_knife.actions.development.npm_manage_packages import OnNpmManagePackages
from harrix_swiss_knife.actions.development.open_config_json import OnOpenConfigJson
from harrix_swiss_knife.actions.development.settings_editor import OnSettingsEditor
from harrix_swiss_knife.actions.development.show_action_usage_stats import OnShowActionUsageStats
from harrix_swiss_knife.actions.development.sync_quick_access_to_total_commander import (
    OnSyncQuickAccessToTotalCommander,
)
from harrix_swiss_knife.actions.development.update_harrix_swiss_knife import OnUpdateHarrixSwissKnife
from harrix_swiss_knife.actions.development.update_node import OnUpdateNode
from harrix_swiss_knife.actions.development.update_uv import OnUpdateUv
from harrix_swiss_knife.actions.development.view_recent_action_logs import OnViewRecentActionLogs
from harrix_swiss_knife.actions.files.all_files_to_parent_folder import OnAllFilesToParentFolder
from harrix_swiss_knife.actions.files.check_featured_image import OnCheckFeaturedImage
from harrix_swiss_knife.actions.files.check_featured_image_in_folders import OnCheckFeaturedImageInFolders
from harrix_swiss_knife.actions.files.combine_for_ai import OnCombineForAI
from harrix_swiss_knife.actions.files.convert_path_to_windows import OnConvertPathToWindows
from harrix_swiss_knife.actions.files.discard_git_changes import OnDiscardGitChanges
from harrix_swiss_knife.actions.files.extract_zip_archives import OnExtractZipArchives
from harrix_swiss_knife.actions.files.git_commit_message import OnGitCommitMessage
from harrix_swiss_knife.actions.files.list_files_current_folder import OnListFilesCurrentFolder
from harrix_swiss_knife.actions.files.list_files_simple import OnListFilesSimple
from harrix_swiss_knife.actions.files.list_files_simple_ignore_hidden_folders import (
    OnListFilesSimpleIgnoreHiddenFolders,
)
from harrix_swiss_knife.actions.files.lock_disks import OnLockDisks
from harrix_swiss_knife.actions.files.remove_empty_folders import OnRemoveEmptyFolders
from harrix_swiss_knife.actions.files.rename_date_in_filenames import OnRenameDateInFilenames
from harrix_swiss_knife.actions.files.rename_fb2_epub_pdf_files import OnRenameFb2EpubPdfFiles
from harrix_swiss_knife.actions.files.rename_files_by_mapping import OnRenameFilesByMapping
from harrix_swiss_knife.actions.files.rename_largest_images_to_featured_image import (
    OnRenameLargestImagesToFeaturedImage,
)
from harrix_swiss_knife.actions.files.tree_view_folder import OnTreeViewFolder
from harrix_swiss_knife.actions.files.tree_view_folder_ignore_hidden_folders import (
    OnTreeViewFolderIgnoreHiddenFolders,
)
from harrix_swiss_knife.actions.images.clear_images import OnClearImages
from harrix_swiss_knife.actions.images.open_images import OnOpenImages
from harrix_swiss_knife.actions.images.open_optimized_images import OnOpenOptimizedImages
from harrix_swiss_knife.actions.images.open_photos_in_viewer import OnOpenPhotosInViewer
from harrix_swiss_knife.actions.images.optimize import OnOptimize
from harrix_swiss_knife.actions.images.optimize_clipboard import OnOptimizeClipboard
from harrix_swiss_knife.actions.images.optimize_clipboard_dialog import OnOptimizeClipboardDialog
from harrix_swiss_knife.actions.images.optimize_dialog_replace import OnOptimizeDialogReplace
from harrix_swiss_knife.actions.images.optimize_quality import OnOptimizeQuality
from harrix_swiss_knife.actions.images.optimize_resize import OnOptimizeResize
from harrix_swiss_knife.actions.images.optimize_single_image import OnOptimizeSingleImage
from harrix_swiss_knife.actions.images.recognize_text_with_ai import OnRecognizeTextWithAI
from harrix_swiss_knife.actions.images.recognize_text_with_ocr import OnRecognizeTextWithOcr
from harrix_swiss_knife.actions.images.screenshot_region import OnScreenshotRegion
from harrix_swiss_knife.actions.markdown.append_yaml_tag import OnAppendYamlTag
from harrix_swiss_knife.actions.markdown.beautify_md import OnBeautifyMd
from harrix_swiss_knife.actions.markdown.beautify_md_and_regenerate_g_md import OnBeautifyMdAndRegenerateGMd
from harrix_swiss_knife.actions.markdown.check_md import OnCheckMd
from harrix_swiss_knife.actions.markdown.decrease_heading_level_content import OnDecreaseHeadingLevelContent
from harrix_swiss_knife.actions.markdown.download_and_replace_images import OnDownloadAndReplaceImages
from harrix_swiss_knife.actions.markdown.fix_md_with_quotes import OnFixMdWithQuotes
from harrix_swiss_knife.actions.markdown.generate_short_note_toc_with_links import OnGenerateShortNoteTocWithLinks
from harrix_swiss_knife.actions.markdown.generate_static_site import OnGenerateStaticSite
from harrix_swiss_knife.actions.markdown.get_list_movies_books import OnGetListMoviesBooks
from harrix_swiss_knife.actions.markdown.get_set_variables_from_yaml import OnGetSetVariablesFromYaml
from harrix_swiss_knife.actions.markdown.increase_heading_level_content import OnIncreaseHeadingLevelContent
from harrix_swiss_knife.actions.markdown.move_md_into_named_folders import OnMoveMdIntoNamedFolders
from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.actions.markdown.optimize_images_in_md import OnOptimizeImagesInMd
from harrix_swiss_knife.actions.markdown.optimize_selected_images import OnOptimizeSelectedImages
from harrix_swiss_knife.actions.markdown.regenerate_g_md import OnRegenerateGMd
from harrix_swiss_knife.actions.markdown.sort_sections import OnSortSections
from harrix_swiss_knife.actions.python.check_python_project import OnCheckPythonProject
from harrix_swiss_knife.actions.python.check_python_projects import OnCheckPythonProjects
from harrix_swiss_knife.actions.python.harrix_check_python import OnHarrixCheckPython
from harrix_swiss_knife.actions.python.new_uv_library import OnNewUvLibrary
from harrix_swiss_knife.actions.python.new_uv_notebook import OnNewUvNotebook
from harrix_swiss_knife.actions.python.new_uv_project import OnNewUvProject
from harrix_swiss_knife.actions.python.publish_python_library import OnPublishPythonLibrary
from harrix_swiss_knife.actions.python.sort_ruff_fmt_docs_python_code import OnSortRuffFmtDocsPythonCode
from harrix_swiss_knife.actions.python.sort_ruff_fmt_python_code import OnSortRuffFmtPythonCode
from harrix_swiss_knife.actions.quick_launcher.action import OnQuickLauncher
from harrix_swiss_knife.actions.site import (
    OnAddSiteContentSubmodule,
    OnFixSiteArticleLinkTitles,
    OnPullSiteSubmodules,
    OnSliceHtmlTemplate,
)
from harrix_swiss_knife.actions.text.fix_text_with_ai import OnFixTextWithAI
from harrix_swiss_knife.actions.text.fix_text_with_ai_from_clipboard import OnFixTextWithAIFromClipboard
from harrix_swiss_knife.actions.text.rewrite_text_with_ai import OnRewriteTextWithAI
from harrix_swiss_knife.actions.text.speech_to_text_with_ai import OnSpeechToTextWithAI
from harrix_swiss_knife.actions.vscode import (
    OnInstallHarrixNotesExplorerExtension,
    OnSyncHarrixNotesExplorer,
    OnVscodeCheck,
    OnVscodeFormat,
)


def get_menu_structure() -> list[Any]:
    """Return the tray menu structure as a nested list of submenus and action classes."""
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
                OnSettingsEditor,
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
                OnRecognizeTextWithOcr,
                OnRecognizeTextWithAI,
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
                OnRegenerateGMd,
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
                OnSliceHtmlTemplate,
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
        OnIcons,
        "-",
        OnQuickLauncher,
        "-",
        OnExit,
    ]
