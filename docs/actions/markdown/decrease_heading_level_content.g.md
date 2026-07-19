---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `decrease_heading_level_content.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnDecreaseHeadingLevelContent`](#️-class-ondecreaseheadinglevelcontent)
  - [⚙️ Method `execute`](#️-method-execute)

</details>

## 🏛️ Class `OnDecreaseHeadingLevelContent`

```python
class OnDecreaseHeadingLevelContent(ActionBase)
```

Decrease the heading level of all headings in Markdown content.

This action takes Markdown content and decreases the level of all headings
by removing one `#` character from each heading, making them one level
shallower in the document hierarchy.

<details>
<summary>Code:</summary>

```python
class OnDecreaseHeadingLevelContent(ActionBase):

    icon = "👈"
    title = "Heading level: Decrease…"

    @ActionBase.handle_exceptions("decreasing heading level")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Decrease the heading level of all headings in Markdown content."""
        content = self.dialogs.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.decrease_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Decrease the heading level of all headings in Markdown content.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        content = self.dialogs.get_text_textarea(
            "Markdown content", "Input Markdown content", "# Title\n\nText\n\n## Subtitle\n\nText"
        )
        if not content:
            return

        new_content = h.md.decrease_heading_level_content(content)
        self.add_line(new_content)
        self.show_result()
```

</details>
