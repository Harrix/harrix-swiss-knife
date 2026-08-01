"""Actions for Markdown file management and related workflows."""

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
from harrix_swiss_knife.actions.markdown.sort_sections import OnSortSections

__all__ = [
    "OnAppendYamlTag",
    "OnBeautifyMd",
    "OnBeautifyMdAndRegenerateGMd",
    "OnCheckMd",
    "OnDecreaseHeadingLevelContent",
    "OnDownloadAndReplaceImages",
    "OnFixMdWithQuotes",
    "OnGenerateShortNoteTocWithLinks",
    "OnGenerateStaticSite",
    "OnGetListMoviesBooks",
    "OnGetSetVariablesFromYaml",
    "OnIncreaseHeadingLevelContent",
    "OnMoveMdIntoNamedFolders",
    "OnNewMarkdown",
    "OnOptimizeImagesInMd",
    "OnOptimizeSelectedImages",
    "OnSortSections",
]
