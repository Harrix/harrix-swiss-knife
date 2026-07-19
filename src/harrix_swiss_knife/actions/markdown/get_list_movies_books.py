"""Actions for Python development and Markdown file management."""

from __future__ import annotations

from typing import Any

from harrix_swiss_knife.actions.base import ActionBase


class OnGetListMoviesBooks(ActionBase):
    """Extract and format a list of movies or books from Markdown content.

    This action takes Markdown content with level-3 headings (`### Title`)
    and converts them into a bulleted list, counting the total number of items.
    Useful for creating web-friendly lists from structured Markdown content.

    """

    icon = "🎬"
    title = "Get a list of movies, books for web…"

    @ActionBase.handle_exceptions("extracting movies/books list")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Extract and format a list of movies or books from Markdown content."""
        default_text = """### Song of the Sea: 8.5

- **Original or English title:** Song of the Sea
- **Date watching:** 2019-10-28
- **Kinopoisk:** <https://www.kinopoisk.ru/film/714248/>
- **IMDb:** <https://www.imdb.com/title/tt1865505/>
- **Comments:** A beautiful cartoon that needs to be shown to children.

### Red Turtle: 9

- **Original or English title:** La tortue rouge
- **Date watching:** 2019-10-12
- **Kinopoisk:** <https://www.kinopoisk.ru/film/879827/>
- **IMDb:** <https://www.imdb.com/title/tt3666024/>
- **Comments:** Beautiful meditative cartoon."""

        content = self.dialogs.get_text_textarea("Markdown content", "Input Markdown content", default_text)
        if not content:
            return

        result = ""
        count = 0
        start_element = "### " if "### " in content else "## "
        for line in content.splitlines():
            if line.startswith(start_element):
                result += f"- {line[4:].strip()}\n"
                count += 1

        result += f"\nCount: {count}"
        self.add_line(result)
        self.show_result()
