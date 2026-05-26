"""Actions for Python development and Markdown file management."""

from harrix_swiss_knife.actions.markdown.append_yaml_tag import OnAppendYamlTag
from harrix_swiss_knife.actions.markdown.beautify_md_folder import OnBeautifyMdFolder
from harrix_swiss_knife.actions.markdown.beautify_md_folder_and_regenerate_g_md import (
    OnBeautifyMdFolderAndRegenerateGMd,
)
from harrix_swiss_knife.actions.markdown.check_md_folder import OnCheckMdFolder
from harrix_swiss_knife.actions.markdown.decrease_heading_level_content import OnDecreaseHeadingLevelContent
from harrix_swiss_knife.actions.markdown.download_and_replace_images_folder import OnDownloadAndReplaceImagesFolder
from harrix_swiss_knife.actions.markdown.fix_md_with_quotes import OnFixMDWithQuotes
from harrix_swiss_knife.actions.markdown.generate_short_note_toc_with_links import OnGenerateShortNoteTocWithLinks
from harrix_swiss_knife.actions.markdown.generate_static_site import OnGenerateStaticSite
from harrix_swiss_knife.actions.markdown.get_list_movies_books import OnGetListMoviesBooks
from harrix_swiss_knife.actions.markdown.get_set_variables_from_yaml import OnGetSetVariablesFromYaml
from harrix_swiss_knife.actions.markdown.increase_heading_level_content import OnIncreaseHeadingLevelContent
from harrix_swiss_knife.actions.markdown.new_markdown import OnNewMarkdown
from harrix_swiss_knife.actions.markdown.optimize_images_folder import OnOptimizeImagesFolder
from harrix_swiss_knife.actions.markdown.optimize_selected_images import OnOptimizeSelectedImages
from harrix_swiss_knife.actions.markdown.sort_sections import OnSortSections

__all__ = [
    "OnAppendYamlTag",
    "OnBeautifyMdFolder",
    "OnBeautifyMdFolderAndRegenerateGMd",
    "OnCheckMdFolder",
    "OnDecreaseHeadingLevelContent",
    "OnDownloadAndReplaceImagesFolder",
    "OnFixMDWithQuotes",
    "OnGenerateShortNoteTocWithLinks",
    "OnGenerateStaticSite",
    "OnGetListMoviesBooks",
    "OnGetSetVariablesFromYaml",
    "OnIncreaseHeadingLevelContent",
    "OnNewMarkdown",
    "OnOptimizeImagesFolder",
    "OnOptimizeSelectedImages",
    "OnSortSections",
]
