---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `text.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `BodyLabel`](#%EF%B8%8F-class-bodylabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `CaptionLabel`](#%EF%B8%8F-class-captionlabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
- [🏛️ Class `DisplayLabel`](#%EF%B8%8F-class-displaylabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-2)
- [🏛️ Class `FluentHyperlinkLabel`](#%EF%B8%8F-class-fluenthyperlinklabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-3)
  - [⚙️ Method `mouseReleaseEvent`](#%EF%B8%8F-method-mousereleaseevent)
  - [⚙️ Method `url`](#%EF%B8%8F-method-url)
- [🏛️ Class `StrongBodyLabel`](#%EF%B8%8F-class-strongbodylabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-4)
- [🏛️ Class `SubtitleLabel`](#%EF%B8%8F-class-subtitlelabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-5)
- [🏛️ Class `TitleLabel`](#%EF%B8%8F-class-titlelabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-6)
- [🏛️ Class `TitleLargeLabel`](#%EF%B8%8F-class-titlelargelabel)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-7)

</details>

## 🏛️ Class `BodyLabel`

```python
class BodyLabel(FluentText)
```

Body text.

<details>
<summary>Code:</summary>

```python
class BodyLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a body label."""
        super().__init__(text, parent, style=TextStyle.BODY)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a body label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.BODY)
```

</details>

## 🏛️ Class `CaptionLabel`

```python
class CaptionLabel(FluentText)
```

Caption text (12 px equivalent, secondary color).

<details>
<summary>Code:</summary>

```python
class CaptionLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a caption label."""
        super().__init__(text, parent, style=TextStyle.CAPTION, role=TextRole.SECONDARY)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a caption label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.CAPTION, role=TextRole.SECONDARY)
```

</details>

## 🏛️ Class `DisplayLabel`

```python
class DisplayLabel(FluentText)
```

Display text (68 px equivalent).

<details>
<summary>Code:</summary>

```python
class DisplayLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a display label."""
        super().__init__(text, parent, style=TextStyle.DISPLAY)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a display label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.DISPLAY)
```

</details>

## 🏛️ Class `FluentHyperlinkLabel`

```python
class FluentHyperlinkLabel(FluentText)
```

Accent-colored text that opens `url` on click.

<details>
<summary>Code:</summary>

```python
class FluentHyperlinkLabel(FluentText):

    def __init__(self, text: str, url: str, parent: QWidget | None = None) -> None:
        """Create a hyperlink label.

        Args:

        - `text` (`str`): Visible text.
        - `url` (`str`): Target URL opened with the system handler.
        - `parent` (`QWidget | None`): Optional parent.

        """
        super().__init__(text, parent, role=TextRole.ACCENT)
        self._url = url
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(url)

    def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001, N802
        """Open the URL on a left click."""
        if event.button() == Qt.MouseButton.LeftButton and self._url:
            QDesktopServices.openUrl(QUrl(self._url))
        super().mouseReleaseEvent(event)

    def url(self) -> str:
        """Return the target URL."""
        return self._url
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str, url: str, parent: QWidget | None = None) -> None
```

Create a hyperlink label.

Args:

- `text` (`str`): Visible text.
- `url` (`str`): Target URL opened with the system handler.
- `parent` (`QWidget | None`): Optional parent.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str, url: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent, role=TextRole.ACCENT)
        self._url = url
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(url)
```

</details>

### ⚙️ Method `mouseReleaseEvent`

```python
def mouseReleaseEvent(self, event) -> None
```

Open the URL on a left click.

<details>
<summary>Code:</summary>

```python
def mouseReleaseEvent(self, event) -> None:  # noqa: ANN001, N802
        if event.button() == Qt.MouseButton.LeftButton and self._url:
            QDesktopServices.openUrl(QUrl(self._url))
        super().mouseReleaseEvent(event)
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

## 🏛️ Class `StrongBodyLabel`

```python
class StrongBodyLabel(FluentText)
```

Semibold body text.

<details>
<summary>Code:</summary>

```python
class StrongBodyLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a semibold body label."""
        super().__init__(text, parent, style=TextStyle.BODY_STRONG)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a semibold body label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.BODY_STRONG)
```

</details>

## 🏛️ Class `SubtitleLabel`

```python
class SubtitleLabel(FluentText)
```

Subtitle text (20 px equivalent, semibold).

<details>
<summary>Code:</summary>

```python
class SubtitleLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a subtitle label."""
        super().__init__(text, parent, style=TextStyle.SUBTITLE)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a subtitle label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.SUBTITLE)
```

</details>

## 🏛️ Class `TitleLabel`

```python
class TitleLabel(FluentText)
```

Title text (28 px equivalent, semibold).

<details>
<summary>Code:</summary>

```python
class TitleLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a title label."""
        super().__init__(text, parent, style=TextStyle.TITLE)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a title label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.TITLE)
```

</details>

## 🏛️ Class `TitleLargeLabel`

```python
class TitleLargeLabel(FluentText)
```

Large title text (40 px equivalent).

<details>
<summary>Code:</summary>

```python
class TitleLargeLabel(FluentText):

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        """Create a large title label."""
        super().__init__(text, parent, style=TextStyle.TITLE_LARGE)
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, text: str = '', parent: QWidget | None = None) -> None
```

Create a large title label.

<details>
<summary>Code:</summary>

```python
def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent, style=TextStyle.TITLE_LARGE)
```

</details>
