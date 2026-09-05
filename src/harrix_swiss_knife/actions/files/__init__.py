"""Actions for file operations and management of directory structures."""

from harrix_swiss_knife.actions.files.all_files_to_parent_folder import OnAllFilesToParentFolder
from harrix_swiss_knife.actions.files.check_featured_image import OnCheckFeaturedImage
from harrix_swiss_knife.actions.files.check_featured_image_in_folders import OnCheckFeaturedImageInFolders
from harrix_swiss_knife.actions.files.check_musicbee_playlists import OnCheckMusicBeePlaylists
from harrix_swiss_knife.actions.files.clean_temporary import OnCleanTemporary
from harrix_swiss_knife.actions.files.close_all_adobe import OnCloseAllAdobe
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
from harrix_swiss_knife.actions.files.sync_chrome_yandex_bookmarks import OnSyncChromeYandexBookmarks
from harrix_swiss_knife.actions.files.tree_view_folder import OnTreeViewFolder
from harrix_swiss_knife.actions.files.tree_view_folder_ignore_hidden_folders import OnTreeViewFolderIgnoreHiddenFolders

__all__ = [
    "OnAllFilesToParentFolder",
    "OnCheckFeaturedImage",
    "OnCheckFeaturedImageInFolders",
    "OnCheckMusicBeePlaylists",
    "OnCleanTemporary",
    "OnCloseAllAdobe",
    "OnCombineForAI",
    "OnConvertPathToWindows",
    "OnDiscardGitChanges",
    "OnExtractZipArchives",
    "OnGitCommitMessage",
    "OnListFilesCurrentFolder",
    "OnListFilesSimple",
    "OnListFilesSimpleIgnoreHiddenFolders",
    "OnLockDisks",
    "OnRemoveEmptyFolders",
    "OnRenameDateInFilenames",
    "OnRenameFb2EpubPdfFiles",
    "OnRenameFilesByMapping",
    "OnRenameLargestImagesToFeaturedImage",
    "OnSyncChromeYandexBookmarks",
    "OnTreeViewFolder",
    "OnTreeViewFolderIgnoreHiddenFolders",
]
