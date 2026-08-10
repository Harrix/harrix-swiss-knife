"""Actions for the main site repository and content submodules."""

from harrix_swiss_knife.actions.site.add_site_content_submodule import OnAddSiteContentSubmodule
from harrix_swiss_knife.actions.site.fix_site_article_link_titles import OnFixSiteArticleLinkTitles
from harrix_swiss_knife.actions.site.pull_site_submodules import OnPullSiteSubmodules
from harrix_swiss_knife.actions.site.slice_html_template import OnSliceHtmlTemplate

__all__ = [
    "OnAddSiteContentSubmodule",
    "OnFixSiteArticleLinkTitles",
    "OnPullSiteSubmodules",
    "OnSliceHtmlTemplate",
]
