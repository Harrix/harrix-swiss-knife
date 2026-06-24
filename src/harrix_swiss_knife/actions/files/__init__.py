"""Actions for file operations and management of directory structures."""

from harrix_swiss_knife.actions.files.all_files_to_parent_folder import OnAllFilesToParentFolder
from harrix_swiss_knife.actions.files.block_disks import OnBlockDisks
from harrix_swiss_knife.actions.files.check_featured_image import OnCheckFeaturedImage
from harrix_swiss_knife.actions.files.check_featured_image_in_folders import OnCheckFeaturedImageInFolders
from harrix_swiss_knife.actions.files.combine_for_ai import OnCombineForAI
from harrix_swiss_knife.actions.files.extract_zip_archives import OnExtractZipArchives
from harrix_swiss_knife.actions.files.list_files_current_folder import OnListFilesCurrentFolder
from harrix_swiss_knife.actions.files.list_files_simple import OnListFilesSimple
from harrix_swiss_knife.actions.files.list_files_simple_ignore_hidden_folders import (
    OnListFilesSimpleIgnoreHiddenFolders,
)
from harrix_swiss_knife.actions.files.remove_empty_folders import OnRemoveEmptyFolders
from harrix_swiss_knife.actions.files.rename_date_in_filenames import OnRenameDateInFilenames
from harrix_swiss_knife.actions.files.rename_fb2_epub_pdf_files import OnRenameFb2EpubPdfFiles
from harrix_swiss_knife.actions.files.rename_files_by_mapping import OnRenameFilesByMapping
from harrix_swiss_knife.actions.files.rename_largest_images_to_featured_image import (
    OnRenameLargestImagesToFeaturedImage,
)
from harrix_swiss_knife.actions.files.rename_last_git_commit_with_emoji import OnRenameLastGitCommitWithEmoji
from harrix_swiss_knife.actions.files.tree_view_folder import OnTreeViewFolder
from harrix_swiss_knife.actions.files.tree_view_folder_ignore_hidden_folders import OnTreeViewFolderIgnoreHiddenFolders

__all__ = [
    "OnAllFilesToParentFolder",
    "OnBlockDisks",
    "OnCheckFeaturedImage",
    "OnCheckFeaturedImageInFolders",
    "OnCombineForAI",
    "OnExtractZipArchives",
    "OnListFilesCurrentFolder",
    "OnListFilesSimple",
    "OnListFilesSimpleIgnoreHiddenFolders",
    "OnRemoveEmptyFolders",
    "OnRenameDateInFilenames",
    "OnRenameFb2EpubPdfFiles",
    "OnRenameFilesByMapping",
    "OnRenameLargestImagesToFeaturedImage",
    "OnRenameLastGitCommitWithEmoji",
    "OnTreeViewFolder",
    "OnTreeViewFolderIgnoreHiddenFolders",
]
