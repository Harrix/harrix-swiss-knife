---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `cards.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentAcrylicUrlCard`](#%EF%B8%8F-class-fluentacrylicurlcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent)
  - [⚙️ Method `url`](#%EF%B8%8F-method-url)
- [🏛️ Class `FluentCommandCard`](#%EF%B8%8F-class-fluentcommandcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `description`](#%EF%B8%8F-method-description)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-1)
  - [⚙️ Method `set_icon`](#%EF%B8%8F-method-set_icon)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint)
  - [⚙️ Method `title`](#%EF%B8%8F-method-title)
- [🏛️ Class `FluentIconTileCard`](#%EF%B8%8F-class-fluenticontilecard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
  - [⚙️ Method `minimumSizeHint`](#%EF%B8%8F-method-minimumsizehint-1)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-2)
  - [⚙️ Method `set_icon`](#%EF%B8%8F-method-set_icon-1)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint-1)
  - [⚙️ Method `title`](#%EF%B8%8F-method-title-1)
- [🏛️ Class `FluentImageCard`](#%EF%B8%8F-class-fluentimagecard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-3)
  - [⚙️ Method `set_pixmap`](#%EF%B8%8F-method-set_pixmap)
- [🏛️ Class `FluentPopularCard`](#%EF%B8%8F-class-fluentpopularcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-4)
- [🏛️ Class `FluentPromotionCard`](#%EF%B8%8F-class-fluentpromotioncard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-5)
- [🏛️ Class `FluentReminderCard`](#%EF%B8%8F-class-fluentremindercard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
- [🏛️ Class `FluentSettingCard`](#%EF%B8%8F-class-fluentsettingcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-7)
  - [⚙️ Method `content`](#%EF%B8%8F-method-content)
  - [⚙️ Method `paintEvent`](#%EF%B8%8F-method-paintevent-6)
  - [⚙️ Method `set_content`](#%EF%B8%8F-method-set_content)
  - [⚙️ Method `set_icon`](#%EF%B8%8F-method-set_icon-2)
  - [⚙️ Method `set_title`](#%EF%B8%8F-method-set_title)
  - [⚙️ Method `sizeHint`](#%EF%B8%8F-method-sizehint-2)
  - [⚙️ Method `title`](#%EF%B8%8F-method-title-2)
  - [⚙️ Method `url`](#%EF%B8%8F-method-url-1)
- [🏛️ Class `FluentSettingEditorCard`](#%EF%B8%8F-class-fluentsettingeditorcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-8)
- [🏛️ Class `FluentSettingHyperlinkCard`](#%EF%B8%8F-class-fluentsettinghyperlinkcard)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-9)
- [🔧 Function `elide_lines`](#-function-elide_lines)

</details>

## 🏛️ Class `FluentAcrylicUrlCard`

```python
class FluentAcrylicUrlCard(FluentInteractiveCard)
```

Compact link card (icon, title, URL) that opens the URL when clicked.

<details>
<summary>Code:</summary>

```python
class FluentAcrylicUrlCard(FluentInteractiveCard):

    def __init__(
        self,
        title: str,
        url: str,
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = "link",
        description: str = "",
    ) -> None:
        """Create a link card."""
        self._title = title
        self._url = url
        self._icon = icon
        self._description = description or url
        super().__init__(parent)
        self.setFixedSize(198, 220)
        self.clicked.connect(self._open)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint an acrylic-like gradient surface with the icon, title, and link glyph."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, with_alpha(palette.accent, 26))
        gradient.setColorAt(1, with_alpha(palette.accent, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), RADIUS_CARD, RADIUS_CARD)
        icon = _icon_for(self._icon, palette, 54)
        if icon is not None:
            icon.paint(painter, QRect(SPACE_XL, SPACE_XL, 54, 54))
        width = self.width() - 2 * SPACE_XL
        title_font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        top = SPACE_XL + 54 + SPACE_L
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        for line in elide_lines(self._title, title_metrics, width, 2):
            painter.drawText(QRect(SPACE_XL, top, width, title_metrics.height()), int(Qt.AlignmentFlag.AlignLeft), line)
            top += title_metrics.height()
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        caption_metrics = QFontMetrics(caption_font)
        for line in elide_lines(self._description, caption_metrics, width, 3):
            painter.drawText(
                QRect(SPACE_XL, top + SPACE_XS, width, caption_metrics.height()), int(Qt.AlignmentFlag.AlignLeft), line
            )
            top += caption_metrics.height()
        link = themed_icon("external-link", palette, palette.text_secondary, ICON_SIZE)
        link.paint(
            painter, self.width() - SPACE_L - ICON_SIZE, self.height() - SPACE_L - ICON_SIZE, ICON_SIZE, ICON_SIZE
        )
        painter.end()

    def url(self) -> str:
        """Return the target URL."""
        return self._url

    def _open(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, url: str, parent: QWidget | None = None, *, icon: QIcon | str | None = 'link', description: str = '') -> None
```

Create a link card.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        url: str,
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = "link",
        description: str = "",
    ) -> None:
        self._title = title
        self._url = url
        self._icon = icon
        self._description = description or url
        super().__init__(parent)
        self.setFixedSize(198, 220)
        self.clicked.connect(self._open)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint an acrylic-like gradient surface with the icon, title, and link glyph.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, with_alpha(palette.accent, 26))
        gradient.setColorAt(1, with_alpha(palette.accent, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), RADIUS_CARD, RADIUS_CARD)
        icon = _icon_for(self._icon, palette, 54)
        if icon is not None:
            icon.paint(painter, QRect(SPACE_XL, SPACE_XL, 54, 54))
        width = self.width() - 2 * SPACE_XL
        title_font = fluent_font(self.font(), TYPE_SUBTITLE, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        top = SPACE_XL + 54 + SPACE_L
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        for line in elide_lines(self._title, title_metrics, width, 2):
            painter.drawText(QRect(SPACE_XL, top, width, title_metrics.height()), int(Qt.AlignmentFlag.AlignLeft), line)
            top += title_metrics.height()
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        caption_metrics = QFontMetrics(caption_font)
        for line in elide_lines(self._description, caption_metrics, width, 3):
            painter.drawText(
                QRect(SPACE_XL, top + SPACE_XS, width, caption_metrics.height()), int(Qt.AlignmentFlag.AlignLeft), line
            )
            top += caption_metrics.height()
        link = themed_icon("external-link", palette, palette.text_secondary, ICON_SIZE)
        link.paint(
            painter, self.width() - SPACE_L - ICON_SIZE, self.height() - SPACE_L - ICON_SIZE, ICON_SIZE, ICON_SIZE
        )
        painter.end()
```

</details>

### ⚙️ Method `url`

```python
def url(self) -> str
```

Return the target URL.

<details>
<summary>Code:</summary>

```python
def url(self) -> str:
        return self._url
```

</details>

## 🏛️ Class `FluentCommandCard`

```python
class FluentCommandCard(FluentInteractiveCard)
```

Command tile: icon on the left, bold title and two-line description.

The tray command window shows every action as one of these. Height comes from
`fluent.tokens`; preferred width is `COMMAND_CARD_WIDTH` and a [`FluentCardGrid`](views.g.md#%EF%B8%8F-class-fluentcardgrid)
assigns the shared column width in its layout pass (no fixed-width thrash).

<details>
<summary>Code:</summary>

```python
class FluentCommandCard(FluentInteractiveCard):

    def __init__(
        self,
        title: str,
        description: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        overline: str = "",
        user_data: object = None,
    ) -> None:
        """Create a command card.

        Args:

        - `title` (`str`): Command title (one line, elided).
        - `description` (`str`): Hint text (two lines, elided).
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`QIcon | str | None`): Ready icon, or a Lucide ID painted in the text color.
        - `overline` (`str`): Small caption above the title (for example the section name).
        - `user_data` (`object`): Arbitrary payload (for example a `QAction`).

        """
        self._title = title
        self._description = description
        self._icon = icon
        self._overline = overline
        self.user_data = user_data
        super().__init__(parent)
        self.setFixedHeight(COMMAND_CARD_HEIGHT)
        self.setMinimumWidth(max(1, int(COMMAND_CARD_WIDTH * COMMAND_CARD_MIN_SCALE)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        tip = "\n".join(part for part in (overline, title, description) if part)
        self.setToolTip(tip)

    def description(self) -> str:
        """Return the description text."""
        return self._description

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Return the smallest width a command grid may squeeze to."""
        return QSize(self.minimumWidth(), COMMAND_CARD_HEIGHT)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the surface, icon, title, and description."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        icon = _icon_for(self._icon, palette, CARD_ICON_SIZE)
        left = SPACE_L
        if icon is not None:
            top = (self.height() - CARD_ICON_SIZE) // 2
            icon.paint(painter, QRect(left, top, CARD_ICON_SIZE, CARD_ICON_SIZE))
            left += CARD_ICON_SIZE + SPACE_L
        width = self.width() - left - SPACE_L
        base = self.font()
        title_font = fluent_font(base, TYPE_BODY, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(base, TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        caption_metrics = QFontMetrics(caption_font)
        overline = (
            caption_metrics.elidedText(self._overline, Qt.TextElideMode.ElideRight, width) if self._overline else ""
        )
        title = title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width)
        max_lines = 1 if overline else 2
        desc_lines = elide_lines(self._description, caption_metrics, width, max_lines) if self._description else []
        height = title_metrics.height() + len(desc_lines) * caption_metrics.height()
        if overline:
            height += caption_metrics.height()
        y = (self.height() - height) / 2
        if overline:
            painter.setFont(caption_font)
            painter.setPen(palette.accent_text)
            painter.drawText(
                QRectF(left, y, width, caption_metrics.height()),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                overline,
            )
            y += caption_metrics.height()
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRectF(left, y, width, title_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            title,
        )
        y += title_metrics.height()
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        for line in desc_lines:
            painter.drawText(
                QRectF(left, y, width, caption_metrics.height()),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                line,
            )
            y += caption_metrics.height()
        painter.end()

    def set_icon(self, icon: QIcon | str | None) -> None:
        """Replace the icon."""
        self._icon = icon
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the preferred command card size before the grid stretches it."""
        return QSize(COMMAND_CARD_WIDTH, COMMAND_CARD_HEIGHT)

    def title(self) -> str:
        """Return the title text."""
        return self._title
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, description: str = '', parent: QWidget | None = None, *, icon: QIcon | str | None = None, overline: str = '', user_data: object = None) -> None
```

Create a command card.

Args:

- `title` (`str`): Command title (one line, elided).
- [`description`](#%EF%B8%8F-method-description) (`str`): Hint text (two lines, elided).
- `parent` (`QWidget | None`): Optional parent.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`QIcon | str | None`): Ready icon, or a Lucide ID painted in the text color.
- `overline` (`str`): Small caption above the title (for example the section name).
- `user_data` (`object`): Arbitrary payload (for example a `QAction`).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        description: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        overline: str = "",
        user_data: object = None,
    ) -> None:
        self._title = title
        self._description = description
        self._icon = icon
        self._overline = overline
        self.user_data = user_data
        super().__init__(parent)
        self.setFixedHeight(COMMAND_CARD_HEIGHT)
        self.setMinimumWidth(max(1, int(COMMAND_CARD_WIDTH * COMMAND_CARD_MIN_SCALE)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        tip = "\n".join(part for part in (overline, title, description) if part)
        self.setToolTip(tip)
```

</details>

### ⚙️ Method `description`

```python
def description(self) -> str
```

Return the description text.

<details>
<summary>Code:</summary>

```python
def description(self) -> str:
        return self._description
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Return the smallest width a command grid may squeeze to.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(self.minimumWidth(), COMMAND_CARD_HEIGHT)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the surface, icon, title, and description.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        icon = _icon_for(self._icon, palette, CARD_ICON_SIZE)
        left = SPACE_L
        if icon is not None:
            top = (self.height() - CARD_ICON_SIZE) // 2
            icon.paint(painter, QRect(left, top, CARD_ICON_SIZE, CARD_ICON_SIZE))
            left += CARD_ICON_SIZE + SPACE_L
        width = self.width() - left - SPACE_L
        base = self.font()
        title_font = fluent_font(base, TYPE_BODY, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(base, TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        caption_metrics = QFontMetrics(caption_font)
        overline = (
            caption_metrics.elidedText(self._overline, Qt.TextElideMode.ElideRight, width) if self._overline else ""
        )
        title = title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width)
        max_lines = 1 if overline else 2
        desc_lines = elide_lines(self._description, caption_metrics, width, max_lines) if self._description else []
        height = title_metrics.height() + len(desc_lines) * caption_metrics.height()
        if overline:
            height += caption_metrics.height()
        y = (self.height() - height) / 2
        if overline:
            painter.setFont(caption_font)
            painter.setPen(palette.accent_text)
            painter.drawText(
                QRectF(left, y, width, caption_metrics.height()),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                overline,
            )
            y += caption_metrics.height()
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRectF(left, y, width, title_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            title,
        )
        y += title_metrics.height()
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        for line in desc_lines:
            painter.drawText(
                QRectF(left, y, width, caption_metrics.height()),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                line,
            )
            y += caption_metrics.height()
        painter.end()
```

</details>

### ⚙️ Method `set_icon`

```python
def set_icon(self, icon: QIcon | str | None) -> None
```

Replace the icon.

<details>
<summary>Code:</summary>

```python
def set_icon(self, icon: QIcon | str | None) -> None:
        self._icon = icon
        self.update()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return the preferred command card size before the grid stretches it.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(COMMAND_CARD_WIDTH, COMMAND_CARD_HEIGHT)
```

</details>

### ⚙️ Method `title`

```python
def title(self) -> str
```

Return the title text.

<details>
<summary>Code:</summary>

```python
def title(self) -> str:
        return self._title
```

</details>

## 🏛️ Class `FluentIconTileCard`

```python
class FluentIconTileCard(FluentInteractiveCard)
```

Compact tile: centered icon above a wrapped title (no description).

Used by Quick launcher and the capture picker. Preferred width is
`ICON_TILE_WIDTH`; a [`FluentCardGrid`](views.g.md#%EF%B8%8F-class-fluentcardgrid) with matching `base_width` assigns the
shared column width.

<details>
<summary>Code:</summary>

```python
class FluentIconTileCard(FluentInteractiveCard):

    _TITLE_LINES = 3

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        user_data: object = None,
    ) -> None:
        """Create an icon tile card.

        Args:

        - `title` (`str`): Label under the icon (up to three wrapped lines).
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`QIcon | str | None`): Ready icon, or a Lucide ID.
        - `user_data` (`object`): Arbitrary payload (for example an action class).

        """
        self._title = title
        self._icon = icon
        self.user_data = user_data
        super().__init__(parent)
        self.setFixedHeight(ICON_TILE_HEIGHT)
        self.setMinimumWidth(max(1, int(ICON_TILE_WIDTH * COMMAND_CARD_MIN_SCALE)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setToolTip(title)

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Return the smallest width a tile grid may squeeze to."""
        return QSize(self.minimumWidth(), ICON_TILE_HEIGHT)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the surface, centered icon, and wrapped title."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = self.rect().adjusted(SPACE_S, SPACE_M, -SPACE_S, -SPACE_M)
        icon = _icon_for(self._icon, palette, ICON_TILE_ICON_SIZE)
        if icon is not None:
            icon_x = rect.left() + max(0, (rect.width() - ICON_TILE_ICON_SIZE) // 2)
            icon.paint(painter, QRect(icon_x, rect.top(), ICON_TILE_ICON_SIZE, ICON_TILE_ICON_SIZE))
        title_font = fluent_font(self.font(), TYPE_CAPTION, weight=QFont.Weight.DemiBold)
        metrics = QFontMetrics(title_font)
        lines = elide_lines(self._title, metrics, rect.width(), self._TITLE_LINES)
        line_height = metrics.height()
        text_top = rect.top() + ICON_TILE_ICON_SIZE + SPACE_S
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        for index, line in enumerate(lines):
            painter.drawText(
                QRect(rect.left(), text_top + index * line_height, rect.width(), line_height),
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                line,
            )
        painter.end()

    def set_icon(self, icon: QIcon | str | None) -> None:
        """Replace the icon."""
        self._icon = icon
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return the preferred tile size before the grid stretches width."""
        return QSize(ICON_TILE_WIDTH, ICON_TILE_HEIGHT)

    def title(self) -> str:
        """Return the title text."""
        return self._title
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None, *, icon: QIcon | str | None = None, user_data: object = None) -> None
```

Create an icon tile card.

Args:

- `title` (`str`): Label under the icon (up to three wrapped lines).
- `parent` (`QWidget | None`): Optional parent.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`QIcon | str | None`): Ready icon, or a Lucide ID.
- `user_data` (`object`): Arbitrary payload (for example an action class).

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        user_data: object = None,
    ) -> None:
        self._title = title
        self._icon = icon
        self.user_data = user_data
        super().__init__(parent)
        self.setFixedHeight(ICON_TILE_HEIGHT)
        self.setMinimumWidth(max(1, int(ICON_TILE_WIDTH * COMMAND_CARD_MIN_SCALE)))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.setToolTip(title)
```

</details>

### ⚙️ Method `minimumSizeHint`

```python
def minimumSizeHint(self) -> QSize
```

Return the smallest width a tile grid may squeeze to.

<details>
<summary>Code:</summary>

```python
def minimumSizeHint(self) -> QSize:  # noqa: N802
        return QSize(self.minimumWidth(), ICON_TILE_HEIGHT)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the surface, centered icon, and wrapped title.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = self.rect().adjusted(SPACE_S, SPACE_M, -SPACE_S, -SPACE_M)
        icon = _icon_for(self._icon, palette, ICON_TILE_ICON_SIZE)
        if icon is not None:
            icon_x = rect.left() + max(0, (rect.width() - ICON_TILE_ICON_SIZE) // 2)
            icon.paint(painter, QRect(icon_x, rect.top(), ICON_TILE_ICON_SIZE, ICON_TILE_ICON_SIZE))
        title_font = fluent_font(self.font(), TYPE_CAPTION, weight=QFont.Weight.DemiBold)
        metrics = QFontMetrics(title_font)
        lines = elide_lines(self._title, metrics, rect.width(), self._TITLE_LINES)
        line_height = metrics.height()
        text_top = rect.top() + ICON_TILE_ICON_SIZE + SPACE_S
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        for index, line in enumerate(lines):
            painter.drawText(
                QRect(rect.left(), text_top + index * line_height, rect.width(), line_height),
                int(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop),
                line,
            )
        painter.end()
```

</details>

### ⚙️ Method `set_icon`

```python
def set_icon(self, icon: QIcon | str | None) -> None
```

Replace the icon.

<details>
<summary>Code:</summary>

```python
def set_icon(self, icon: QIcon | str | None) -> None:
        self._icon = icon
        self.update()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return the preferred tile size before the grid stretches width.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(ICON_TILE_WIDTH, ICON_TILE_HEIGHT)
```

</details>

### ⚙️ Method `title`

```python
def title(self) -> str
```

Return the title text.

<details>
<summary>Code:</summary>

```python
def title(self) -> str:
        return self._title
```

</details>

## 🏛️ Class `FluentImageCard`

```python
class FluentImageCard(FluentInteractiveCard)
```

Card with an image on top and a title / caption below.

<details>
<summary>Code:</summary>

```python
class FluentImageCard(FluentInteractiveCard):

    def __init__(
        self, title: str, caption: str = "", parent: QWidget | None = None, *, pixmap: QPixmap | None = None
    ) -> None:
        """Create an image card."""
        self._title = title
        self._caption = caption
        self._pixmap = pixmap
        super().__init__(parent)
        self.setFixedSize(240, _IMAGE_CARD_HEIGHT)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the clipped image and text."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        image_rect = QRectF(1, 1, self.width() - 2, self.height() * 0.6)
        painter.save()
        painter.setClipPath(rounded_path(image_rect.adjusted(0, 0, 0, RADIUS_CARD), RADIUS_CARD))
        painter.setClipRect(image_rect, Qt.ClipOperation.IntersectClip)
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                image_rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(image_rect.topLeft(), scaled)
        else:
            painter.fillRect(image_rect, palette.subtle_hover)
            icon = themed_icon("image", palette, palette.text_tertiary, ICON_SIZE_LARGE)
            center = image_rect.center()
            icon.paint(
                painter,
                int(center.x() - ICON_SIZE_LARGE / 2),
                int(center.y() - ICON_SIZE_LARGE / 2),
                ICON_SIZE_LARGE,
                ICON_SIZE_LARGE,
            )
        painter.restore()
        text_top = int(image_rect.bottom()) + SPACE_S
        width = self.width() - 2 * SPACE_M
        title_font = fluent_font(self.font(), TYPE_BODY, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRect(SPACE_M, text_top, width, title_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width),
        )
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        caption_metrics = QFontMetrics(caption_font)
        painter.drawText(
            QRect(SPACE_M, text_top + title_metrics.height(), width, caption_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            caption_metrics.elidedText(self._caption, Qt.TextElideMode.ElideRight, width),
        )
        painter.end()

    def set_pixmap(self, pixmap: QPixmap | None) -> None:
        """Replace the image."""
        self._pixmap = pixmap
        self.update()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, caption: str = '', parent: QWidget | None = None, *, pixmap: QPixmap | None = None) -> None
```

Create an image card.

<details>
<summary>Code:</summary>

```python
def __init__(
        self, title: str, caption: str = "", parent: QWidget | None = None, *, pixmap: QPixmap | None = None
    ) -> None:
        self._title = title
        self._caption = caption
        self._pixmap = pixmap
        super().__init__(parent)
        self.setFixedSize(240, _IMAGE_CARD_HEIGHT)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the clipped image and text.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        image_rect = QRectF(1, 1, self.width() - 2, self.height() * 0.6)
        painter.save()
        painter.setClipPath(rounded_path(image_rect.adjusted(0, 0, 0, RADIUS_CARD), RADIUS_CARD))
        painter.setClipRect(image_rect, Qt.ClipOperation.IntersectClip)
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                image_rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.drawPixmap(image_rect.topLeft(), scaled)
        else:
            painter.fillRect(image_rect, palette.subtle_hover)
            icon = themed_icon("image", palette, palette.text_tertiary, ICON_SIZE_LARGE)
            center = image_rect.center()
            icon.paint(
                painter,
                int(center.x() - ICON_SIZE_LARGE / 2),
                int(center.y() - ICON_SIZE_LARGE / 2),
                ICON_SIZE_LARGE,
                ICON_SIZE_LARGE,
            )
        painter.restore()
        text_top = int(image_rect.bottom()) + SPACE_S
        width = self.width() - 2 * SPACE_M
        title_font = fluent_font(self.font(), TYPE_BODY, weight=QFont.Weight.DemiBold)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRect(SPACE_M, text_top, width, title_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width),
        )
        painter.setFont(caption_font)
        painter.setPen(palette.text_secondary)
        caption_metrics = QFontMetrics(caption_font)
        painter.drawText(
            QRect(SPACE_M, text_top + title_metrics.height(), width, caption_metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            caption_metrics.elidedText(self._caption, Qt.TextElideMode.ElideRight, width),
        )
        painter.end()
```

</details>

### ⚙️ Method `set_pixmap`

```python
def set_pixmap(self, pixmap: QPixmap | None) -> None
```

Replace the image.

<details>
<summary>Code:</summary>

```python
def set_pixmap(self, pixmap: QPixmap | None) -> None:
        self._pixmap = pixmap
        self.update()
```

</details>

## 🏛️ Class `FluentPopularCard`

```python
class FluentPopularCard(FluentInteractiveCard)
```

Square-ish tile: large icon, title, caption, and a hover reveal of the details.

<details>
<summary>Code:</summary>

```python
class FluentPopularCard(FluentInteractiveCard):

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        details: str = "",
    ) -> None:
        """Create a popular-item card."""
        self._title = title
        self._subtitle = subtitle
        self._icon = icon
        self._details = details
        super().__init__(parent)
        self.setFixedSize(200, 160)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint icon and text; show details while hovered."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = self.rect().adjusted(SPACE_L, SPACE_L, -SPACE_L, -SPACE_L)
        base = self.font()
        caption = fluent_font(base, TYPE_CAPTION)
        if self._hovered and self._details:
            painter.setFont(caption)
            painter.setPen(palette.text_secondary)
            painter.drawText(
                rect,
                int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop),
                self._details,
            )
            painter.end()
            return
        icon = _icon_for(self._icon, palette, CARD_ICON_SIZE)
        if icon is not None:
            icon.paint(painter, QRect(rect.left(), rect.top(), CARD_ICON_SIZE, CARD_ICON_SIZE))
        title_font = fluent_font(base, TYPE_BODY, weight=QFont.Weight.DemiBold)
        metrics = QFontMetrics(title_font)
        top = rect.top() + CARD_ICON_SIZE + SPACE_M
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRect(rect.left(), top, rect.width(), metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, rect.width()),
        )
        painter.setFont(caption)
        painter.setPen(palette.text_secondary)
        lines = elide_lines(self._subtitle, QFontMetrics(caption), rect.width(), 2)
        line_height = QFontMetrics(caption).height()
        for index, line in enumerate(lines):
            painter.drawText(
                QRect(rect.left(), top + metrics.height() + SPACE_XS + index * line_height, rect.width(), line_height),
                int(Qt.AlignmentFlag.AlignLeft),
                line,
            )
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, subtitle: str = '', parent: QWidget | None = None, *, icon: QIcon | str | None = None, details: str = '') -> None
```

Create a popular-item card.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        details: str = "",
    ) -> None:
        self._title = title
        self._subtitle = subtitle
        self._icon = icon
        self._details = details
        super().__init__(parent)
        self.setFixedSize(200, 160)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint icon and text; show details while hovered.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = self.rect().adjusted(SPACE_L, SPACE_L, -SPACE_L, -SPACE_L)
        base = self.font()
        caption = fluent_font(base, TYPE_CAPTION)
        if self._hovered and self._details:
            painter.setFont(caption)
            painter.setPen(palette.text_secondary)
            painter.drawText(
                rect,
                int(Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop),
                self._details,
            )
            painter.end()
            return
        icon = _icon_for(self._icon, palette, CARD_ICON_SIZE)
        if icon is not None:
            icon.paint(painter, QRect(rect.left(), rect.top(), CARD_ICON_SIZE, CARD_ICON_SIZE))
        title_font = fluent_font(base, TYPE_BODY, weight=QFont.Weight.DemiBold)
        metrics = QFontMetrics(title_font)
        top = rect.top() + CARD_ICON_SIZE + SPACE_M
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRect(rect.left(), top, rect.width(), metrics.height()),
            int(Qt.AlignmentFlag.AlignLeft),
            metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, rect.width()),
        )
        painter.setFont(caption)
        painter.setPen(palette.text_secondary)
        lines = elide_lines(self._subtitle, QFontMetrics(caption), rect.width(), 2)
        line_height = QFontMetrics(caption).height()
        for index, line in enumerate(lines):
            painter.drawText(
                QRect(rect.left(), top + metrics.height() + SPACE_XS + index * line_height, rect.width(), line_height),
                int(Qt.AlignmentFlag.AlignLeft),
                line,
            )
        painter.end()
```

</details>

## 🏛️ Class `FluentPromotionCard`

```python
class FluentPromotionCard(FluentInteractiveCard)
```

Wide banner card: gradient or image background, title, text, and an action button.

<details>
<summary>Code:</summary>

```python
class FluentPromotionCard(FluentInteractiveCard):

    action_clicked = Signal()

    def __init__(
        self,
        title: str,
        text: str = "",
        parent: QWidget | None = None,
        *,
        action_text: str = "",
        pixmap: QPixmap | None = None,
    ) -> None:
        """Create a promotion banner."""
        self._pixmap = pixmap
        super().__init__(parent)
        self.setMinimumHeight(_PROMOTION_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        layout.setSpacing(SPACE_S)
        layout.addWidget(FluentText(title, self, style=TextStyle.TITLE))
        if text:
            layout.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        layout.addStretch(1)
        if action_text:
            button = FluentPrimaryButton(action_text, self)
            button.clicked.connect(self.action_clicked)
            row = QHBoxLayout()
            row.addWidget(button)
            row.addStretch(1)
            layout.addLayout(row)

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the gradient (or image) background."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.setClipPath(rounded_path(rect, RADIUS_CARD))
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.setOpacity(0.35)
            painter.drawPixmap(rect.topLeft(), scaled)
        else:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, with_alpha(palette.accent, 46))
            gradient.setColorAt(1, with_alpha(palette.accent, 4))
            painter.fillRect(rect, gradient)
        painter.end()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, text: str = '', parent: QWidget | None = None, *, action_text: str = '', pixmap: QPixmap | None = None) -> None
```

Create a promotion banner.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        text: str = "",
        parent: QWidget | None = None,
        *,
        action_text: str = "",
        pixmap: QPixmap | None = None,
    ) -> None:
        self._pixmap = pixmap
        super().__init__(parent)
        self.setMinimumHeight(_PROMOTION_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_XL, SPACE_XL, SPACE_XL, SPACE_XL)
        layout.setSpacing(SPACE_S)
        layout.addWidget(FluentText(title, self, style=TextStyle.TITLE))
        if text:
            layout.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        layout.addStretch(1)
        if action_text:
            button = FluentPrimaryButton(action_text, self)
            button.clicked.connect(self.action_clicked)
            row = QHBoxLayout()
            row.addWidget(button)
            row.addStretch(1)
            layout.addLayout(row)
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the gradient (or image) background.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.setClipPath(rounded_path(rect, RADIUS_CARD))
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                rect.size().toSize(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.setOpacity(0.35)
            painter.drawPixmap(rect.topLeft(), scaled)
        else:
            gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
            gradient.setColorAt(0, with_alpha(palette.accent, 46))
            gradient.setColorAt(1, with_alpha(palette.accent, 4))
            painter.fillRect(rect, gradient)
        painter.end()
```

</details>

## 🏛️ Class `FluentReminderCard`

```python
class FluentReminderCard(FluentCard)
```

Reminder row: severity icon, title, time caption, and a dismiss button.

<details>
<summary>Code:</summary>

```python
class FluentReminderCard(FluentCard):

    dismissed = Signal()

    def __init__(
        self, title: str, when: str = "", parent: QWidget | None = None, *, icon: str = "bell", text: str = ""
    ) -> None:
        """Create a reminder card."""
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_M, SPACE_S, SPACE_M)
        row.setSpacing(SPACE_M)
        self._icon_name = icon
        self._icon_widget = _IconView(icon, self)
        row.addWidget(self._icon_widget, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(2)
        column.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG))
        if text:
            column.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        if when:
            column.addWidget(CaptionLabel(when, self))
        row.addLayout(column, 1)
        close = FluentIconButton("x", self, tooltip="Dismiss")
        close.clicked.connect(self._dismiss)
        row.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)

    def _dismiss(self) -> None:
        self.dismissed.emit()
        self.hide()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, when: str = '', parent: QWidget | None = None, *, icon: str = 'bell', text: str = '') -> None
```

Create a reminder card.

<details>
<summary>Code:</summary>

```python
def __init__(
        self, title: str, when: str = "", parent: QWidget | None = None, *, icon: str = "bell", text: str = ""
    ) -> None:
        super().__init__(parent)
        row = QHBoxLayout(self)
        row.setContentsMargins(SPACE_L, SPACE_M, SPACE_S, SPACE_M)
        row.setSpacing(SPACE_M)
        self._icon_name = icon
        self._icon_widget = _IconView(icon, self)
        row.addWidget(self._icon_widget, 0, Qt.AlignmentFlag.AlignTop)
        column = QVBoxLayout()
        column.setSpacing(2)
        column.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG))
        if text:
            column.addWidget(FluentText(text, self, role=TextRole.SECONDARY, word_wrap=True))
        if when:
            column.addWidget(CaptionLabel(when, self))
        row.addLayout(column, 1)
        close = FluentIconButton("x", self, tooltip="Dismiss")
        close.clicked.connect(self._dismiss)
        row.addWidget(close, 0, Qt.AlignmentFlag.AlignTop)
```

</details>

## 🏛️ Class `FluentSettingCard`

```python
class FluentSettingCard(FluentInteractiveCard)
```

Full-width Windows Settings row: icon, title, description, and a trailing chevron.

Stack these inside [`FluentGroupBox`](navigation.g.md#%EF%B8%8F-class-fluentgroupbox) for Settings-style category lists. Click
emits `clicked`; set `url` (or use [`FluentSettingHyperlinkCard`](#%EF%B8%8F-class-fluentsettinghyperlinkcard)) to open a link.

<details>
<summary>Code:</summary>

```python
class FluentSettingCard(FluentInteractiveCard):

    def __init__(
        self,
        title: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        url: str = "",
        trailing_icon: str = "chevron-right",
        user_data: object = None,
    ) -> None:
        """Create a setting / navigation card.

        Args:

        - `title` (`str`): Primary label (one line, elided).
        - `content` (`str`): Secondary description (one line, elided).
        - `parent` (`QWidget | None`): Optional parent.
        - `icon` (`QIcon | str | None`): Ready icon, or a Lucide ID.
        - `url` (`str`): When set, clicking also opens this URL.
        - `trailing_icon` (`str`): Lucide ID on the right (`chevron-right` by default).
        - `user_data` (`object`): Arbitrary payload for the click handler.

        """
        self._title = title
        self._content = content
        self._icon = icon
        self._url = url
        self._trailing_icon = trailing_icon
        self.user_data = user_data
        super().__init__(parent)
        height = SETTING_CARD_HEIGHT if content else SETTING_CARD_HEIGHT_COMPACT
        self.setFixedHeight(height)
        self.setMinimumWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tip = "\n".join(part for part in (title, content, url) if part)
        self.setToolTip(tip)
        if url:
            self.clicked.connect(self._open_url)

    def content(self) -> str:
        """Return the secondary description text."""
        return self._content

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint the surface, leading icon, title/content, and trailing glyph."""
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        left = SPACE_L
        icon = _icon_for(self._icon, palette, ICON_SIZE_LARGE)
        if icon is not None:
            icon.paint(
                painter,
                QRect(left, (self.height() - ICON_SIZE_LARGE) // 2, ICON_SIZE_LARGE, ICON_SIZE_LARGE),
            )
            left += ICON_SIZE_LARGE + SPACE_L
        trailing = SPACE_L + ICON_SIZE
        width = max(0, self.width() - left - trailing - SPACE_S)
        title_font = fluent_font(self.font(), TYPE_BODY)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        caption_metrics = QFontMetrics(caption_font)
        title = title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width)
        content = caption_metrics.elidedText(self._content, Qt.TextElideMode.ElideRight, width) if self._content else ""
        body_h = title_metrics.height()
        caption_h = caption_metrics.height() if content else 0
        y = (self.height() - body_h - caption_h) / 2
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRectF(left, y, width, body_h),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            title,
        )
        if content:
            painter.setFont(caption_font)
            painter.setPen(palette.text_secondary)
            painter.drawText(
                QRectF(left, y + body_h, width, caption_h),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                content,
            )
        themed_icon(self._trailing_icon, palette, palette.text_secondary, ICON_SIZE).paint(
            painter,
            self.width() - SPACE_L - ICON_SIZE,
            (self.height() - ICON_SIZE) // 2,
            ICON_SIZE,
            ICON_SIZE,
        )
        painter.end()

    def set_content(self, content: str) -> None:
        """Replace the secondary description and adjust height."""
        self._content = content
        self.setFixedHeight(SETTING_CARD_HEIGHT if content else SETTING_CARD_HEIGHT_COMPACT)
        self.update()

    def set_icon(self, icon: QIcon | str | None) -> None:
        """Replace the leading icon."""
        self._icon = icon
        self.update()

    def set_title(self, title: str) -> None:
        """Replace the title text."""
        self._title = title
        self.update()

    def sizeHint(self) -> QSize:  # noqa: N802
        """Return a wide settings-row size."""
        return QSize(480, self.height())

    def title(self) -> str:
        """Return the title text."""
        return self._title

    def url(self) -> str:
        """Return the optional URL opened on click."""
        return self._url

    def _open_url(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, content: str = '', parent: QWidget | None = None, *, icon: QIcon | str | None = None, url: str = '', trailing_icon: str = 'chevron-right', user_data: object = None) -> None
```

Create a setting / navigation card.

Args:

- `title` (`str`): Primary label (one line, elided).
- [`content`](#%EF%B8%8F-method-content) (`str`): Secondary description (one line, elided).
- `parent` (`QWidget | None`): Optional parent.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`QIcon | str | None`): Ready icon, or a Lucide ID.
- `url` (`str`): When set, clicking also opens this URL.
- `trailing_icon` (`str`): Lucide ID on the right (`chevron-right` by default).
- `user_data` (`object`): Arbitrary payload for the click handler.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = None,
        url: str = "",
        trailing_icon: str = "chevron-right",
        user_data: object = None,
    ) -> None:
        self._title = title
        self._content = content
        self._icon = icon
        self._url = url
        self._trailing_icon = trailing_icon
        self.user_data = user_data
        super().__init__(parent)
        height = SETTING_CARD_HEIGHT if content else SETTING_CARD_HEIGHT_COMPACT
        self.setFixedHeight(height)
        self.setMinimumWidth(280)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        tip = "\n".join(part for part in (title, content, url) if part)
        self.setToolTip(tip)
        if url:
            self.clicked.connect(self._open_url)
```

</details>

### ⚙️ Method `content`

```python
def content(self) -> str
```

Return the secondary description text.

<details>
<summary>Code:</summary>

```python
def content(self) -> str:
        return self._content
```

</details>

### ⚙️ Method `paintEvent`

```python
def paintEvent(self, _event: QPaintEvent) -> None
```

Paint the surface, leading icon, title/content, and trailing glyph.

<details>
<summary>Code:</summary>

```python
def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        palette = palette_for(self)
        painter = antialiased_painter(self)
        self.paint_background(painter, palette)
        left = SPACE_L
        icon = _icon_for(self._icon, palette, ICON_SIZE_LARGE)
        if icon is not None:
            icon.paint(
                painter,
                QRect(left, (self.height() - ICON_SIZE_LARGE) // 2, ICON_SIZE_LARGE, ICON_SIZE_LARGE),
            )
            left += ICON_SIZE_LARGE + SPACE_L
        trailing = SPACE_L + ICON_SIZE
        width = max(0, self.width() - left - trailing - SPACE_S)
        title_font = fluent_font(self.font(), TYPE_BODY)
        caption_font = fluent_font(self.font(), TYPE_CAPTION)
        title_metrics = QFontMetrics(title_font)
        caption_metrics = QFontMetrics(caption_font)
        title = title_metrics.elidedText(self._title, Qt.TextElideMode.ElideRight, width)
        content = caption_metrics.elidedText(self._content, Qt.TextElideMode.ElideRight, width) if self._content else ""
        body_h = title_metrics.height()
        caption_h = caption_metrics.height() if content else 0
        y = (self.height() - body_h - caption_h) / 2
        painter.setFont(title_font)
        painter.setPen(palette.text_primary)
        painter.drawText(
            QRectF(left, y, width, body_h),
            int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
            title,
        )
        if content:
            painter.setFont(caption_font)
            painter.setPen(palette.text_secondary)
            painter.drawText(
                QRectF(left, y + body_h, width, caption_h),
                int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                content,
            )
        themed_icon(self._trailing_icon, palette, palette.text_secondary, ICON_SIZE).paint(
            painter,
            self.width() - SPACE_L - ICON_SIZE,
            (self.height() - ICON_SIZE) // 2,
            ICON_SIZE,
            ICON_SIZE,
        )
        painter.end()
```

</details>

### ⚙️ Method `set_content`

```python
def set_content(self, content: str) -> None
```

Replace the secondary description and adjust height.

<details>
<summary>Code:</summary>

```python
def set_content(self, content: str) -> None:
        self._content = content
        self.setFixedHeight(SETTING_CARD_HEIGHT if content else SETTING_CARD_HEIGHT_COMPACT)
        self.update()
```

</details>

### ⚙️ Method `set_icon`

```python
def set_icon(self, icon: QIcon | str | None) -> None
```

Replace the leading icon.

<details>
<summary>Code:</summary>

```python
def set_icon(self, icon: QIcon | str | None) -> None:
        self._icon = icon
        self.update()
```

</details>

### ⚙️ Method `set_title`

```python
def set_title(self, title: str) -> None
```

Replace the title text.

<details>
<summary>Code:</summary>

```python
def set_title(self, title: str) -> None:
        self._title = title
        self.update()
```

</details>

### ⚙️ Method `sizeHint`

```python
def sizeHint(self) -> QSize
```

Return a wide settings-row size.

<details>
<summary>Code:</summary>

```python
def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(480, self.height())
```

</details>

### ⚙️ Method `title`

```python
def title(self) -> str
```

Return the title text.

<details>
<summary>Code:</summary>

```python
def title(self) -> str:
        return self._title
```

</details>

### ⚙️ Method `url`

```python
def url(self) -> str
```

Return the optional URL opened on click.

<details>
<summary>Code:</summary>

```python
def url(self) -> str:
        return self._url
```

</details>

## 🏛️ Class `FluentSettingEditorCard`

```python
class FluentSettingEditorCard(FluentCard)
```

Windows Settings detail card: title, optional description, and an editor body.

Use `trailing_layout` for compact controls (toggle, Save) and [`body_layout`](../../apps/common/chart_widgets.g.md#%EF%B8%8F-method-body_layout) for
the main field. Unlike [`FluentSettingCard`](#%EF%B8%8F-class-fluentsettingcard), this is not a navigation row.

<details>
<summary>Code:</summary>

```python
class FluentSettingEditorCard(FluentCard):

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        description: str = "",
        icon: str = "",
    ) -> None:
        """Create an editor setting card.

        Args:

        - `title` (`str`): Primary label.
        - `parent` (`QWidget | None`): Optional parent.
        - `description` (`str`): Secondary caption under the title.
        - `icon` (`str`): Optional Lucide ID on the left.

        """
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_M)
        root.setSpacing(SPACE_S)
        header = QHBoxLayout()
        header.setSpacing(SPACE_M)
        if icon:
            header.addWidget(_IconView(icon, self), 0, Qt.AlignmentFlag.AlignTop)
        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        text_column.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG))
        if description:
            text_column.addWidget(FluentText(description, self, role=TextRole.SECONDARY, word_wrap=True))
        header.addLayout(text_column, 1)
        self.trailing_layout = QHBoxLayout()
        self.trailing_layout.setSpacing(SPACE_S)
        self.trailing_layout.setContentsMargins(0, 0, 0, 0)
        header.addLayout(self.trailing_layout, 0)
        root.addLayout(header)
        self.body_layout = QVBoxLayout()
        self.body_layout.setSpacing(SPACE_S)
        self.body_layout.setContentsMargins(ICON_SIZE_LARGE + SPACE_M if icon else 0, 0, 0, 0)
        root.addLayout(self.body_layout)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, parent: QWidget | None = None, *, description: str = '', icon: str = '') -> None
```

Create an editor setting card.

Args:

- `title` (`str`): Primary label.
- `parent` (`QWidget | None`): Optional parent.
- [`description`](#%EF%B8%8F-method-description) (`str`): Secondary caption under the title.
- [`icon`](../../qt_split_menu_button.g.md#%EF%B8%8F-method-icon) (`str`): Optional Lucide ID on the left.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        description: str = "",
        icon: str = "",
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        root = QVBoxLayout(self)
        root.setContentsMargins(SPACE_L, SPACE_M, SPACE_L, SPACE_M)
        root.setSpacing(SPACE_S)
        header = QHBoxLayout()
        header.setSpacing(SPACE_M)
        if icon:
            header.addWidget(_IconView(icon, self), 0, Qt.AlignmentFlag.AlignTop)
        text_column = QVBoxLayout()
        text_column.setSpacing(2)
        text_column.addWidget(FluentText(title, self, style=TextStyle.BODY_STRONG))
        if description:
            text_column.addWidget(FluentText(description, self, role=TextRole.SECONDARY, word_wrap=True))
        header.addLayout(text_column, 1)
        self.trailing_layout = QHBoxLayout()
        self.trailing_layout.setSpacing(SPACE_S)
        self.trailing_layout.setContentsMargins(0, 0, 0, 0)
        header.addLayout(self.trailing_layout, 0)
        root.addLayout(header)
        self.body_layout = QVBoxLayout()
        self.body_layout.setSpacing(SPACE_S)
        self.body_layout.setContentsMargins(ICON_SIZE_LARGE + SPACE_M if icon else 0, 0, 0, 0)
        root.addLayout(self.body_layout)
```

</details>

## 🏛️ Class `FluentSettingHyperlinkCard`

```python
class FluentSettingHyperlinkCard(FluentSettingCard)
```

Settings-style row that opens a URL (trailing `external-link` glyph).

<details>
<summary>Code:</summary>

```python
class FluentSettingHyperlinkCard(FluentSettingCard):

    def __init__(
        self,
        title: str,
        url: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = "link",
        user_data: object = None,
    ) -> None:
        """Create a hyperlink setting card."""
        super().__init__(
            title,
            content or url,
            parent,
            icon=icon,
            url=url,
            trailing_icon="external-link",
            user_data=user_data,
        )
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, title: str, url: str, content: str = '', parent: QWidget | None = None, *, icon: QIcon | str | None = 'link', user_data: object = None) -> None
```

Create a hyperlink setting card.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        title: str,
        url: str,
        content: str = "",
        parent: QWidget | None = None,
        *,
        icon: QIcon | str | None = "link",
        user_data: object = None,
    ) -> None:
        super().__init__(
            title,
            content or url,
            parent,
            icon=icon,
            url=url,
            trailing_icon="external-link",
            user_data=user_data,
        )
```

</details>

## 🔧 Function `elide_lines`

```python
def elide_lines(text: str, metrics: QFontMetrics, width: int, max_lines: int) -> list[str]
```

Word-wrap `text` to `width` and elide the last of at most `max_lines` lines.

Args:

- `text` (`str`): Source text.
- `metrics` (`QFontMetrics`): Metrics of the font the text is painted with.
- `width` (`int`): Available width in pixels.
- `max_lines` (`int`): Maximum number of lines.

Returns:

- `list[str]`: Lines ready to paint.

<details>
<summary>Code:</summary>

```python
def elide_lines(text: str, metrics: QFontMetrics, width: int, max_lines: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    index = 0
    while index < len(words):
        candidate = f"{current} {words[index]}".strip()
        if metrics.horizontalAdvance(candidate) <= width or not current:
            current = candidate
            index += 1
            continue
        lines.append(current)
        current = ""
        if len(lines) == max_lines - 1:
            break
    rest = " ".join([current, *words[index:]]).strip() if len(lines) == max_lines - 1 else current
    if rest:
        lines.append(metrics.elidedText(rest, Qt.TextElideMode.ElideRight, width))
    return lines[:max_lines]
```

</details>
