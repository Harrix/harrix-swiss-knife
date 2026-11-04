---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `about_fluent_dialog.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `FluentAboutDialog`](#%EF%B8%8F-class-fluentaboutdialog)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `clipboard_text`](#%EF%B8%8F-method-clipboard_text)

</details>

## 🏛️ Class `FluentAboutDialog`

```python
class FluentAboutDialog(FluentDialog)
```

Centered logo, Fluent type ramp, Copy and OK footer.

<details>
<summary>Code:</summary>

```python
class FluentAboutDialog(FluentDialog):

    def __init__(
        self,
        *,
        app_name: str,
        version: str,
        description: str,
        author: str,
        license_text: str,
        github: str,
        parent: QWidget | None = None,
        window_title: str = "About",
        on_copied: Callable[[], None] | None = None,
    ) -> None:
        """Build the About content and a Copy button beside OK."""
        super().__init__(window_title, "", parent, primary_text="OK", secondary_text="")
        self._on_copied = on_copied
        self._clipboard_text = _clipboard_text(
            app_name=app_name,
            version=version,
            description=description,
            author=author,
            license_text=license_text,
            github=github,
        )

        self._body.title_label.hide()
        self._body.content_label.hide()
        self.content_layout.setSpacing(SPACE_S)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo = QLabel(self)
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        logo.setPixmap(QIcon(_ABOUT_LOGO_RESOURCE).pixmap(_ABOUT_LOGO_SIZE, _ABOUT_LOGO_SIZE))
        logo.setFixedHeight(_ABOUT_LOGO_SIZE + SPACE_XS)
        self.content_layout.addWidget(logo)

        name = TitleLabel(app_name, self)
        name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        name.setWordWrap(True)
        self.content_layout.addWidget(name)

        if version:
            version_label = CaptionLabel(f"Version {version}", self)
            version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.content_layout.addWidget(version_label)

        self.content_layout.addSpacing(SPACE_S)

        if description:
            body = BodyLabel(description.replace("\n", " ").strip(), self)
            body.setWordWrap(True)
            body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.content_layout.addWidget(body)
            self.content_layout.addSpacing(SPACE_L)

        if author:
            self._add_meta_row("Author", author)
        if license_text:
            self._add_meta_row("License", license_text)
        if github:
            self.content_layout.addWidget(StrongBodyLabel("GitHub", self))
            link = FluentHyperlinkLabel(github, github, self)
            link.setWordWrap(True)
            self.content_layout.addWidget(link)

        copy_button = FluentPushButton("Copy", self._body.footer, icon="copy")
        copy_button.clicked.connect(self._copy_to_clipboard)
        self._body.footer.row.insertWidget(0, copy_button, 1)

    def clipboard_text(self) -> str:
        """Return the plain-text About block used for Copy."""
        return self._clipboard_text

    def _add_meta_row(self, label: str, value: str) -> None:
        self.content_layout.addWidget(StrongBodyLabel(label, self))
        value_label = BodyLabel(value, self)
        value_label.setWordWrap(True)
        self.content_layout.addWidget(value_label)
        self.content_layout.addSpacing(SPACE_S)

    def _copy_to_clipboard(self) -> None:
        QGuiApplication.clipboard().setText(self._clipboard_text)
        if self._on_copied is not None:
            self._on_copied()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, *, app_name: str, version: str, description: str, author: str, license_text: str, github: str, parent: QWidget | None = None, window_title: str = 'About', on_copied: Callable[[], None] | None = None) -> None
```

Build the About content and a Copy button beside OK.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        *,
        app_name: str,
        version: str,
        description: str,
        author: str,
        license_text: str,
        github: str,
        parent: QWidget | None = None,
        window_title: str = "About",
        on_copied: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(window_title, "", parent, primary_text="OK", secondary_text="")
        self._on_copied = on_copied
        self._clipboard_text = _clipboard_text(
            app_name=app_name,
            version=version,
            description=description,
            author=author,
            license_text=license_text,
            github=github,
        )

        self._body.title_label.hide()
        self._body.content_label.hide()
        self.content_layout.setSpacing(SPACE_S)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        logo = QLabel(self)
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        logo.setPixmap(QIcon(_ABOUT_LOGO_RESOURCE).pixmap(_ABOUT_LOGO_SIZE, _ABOUT_LOGO_SIZE))
        logo.setFixedHeight(_ABOUT_LOGO_SIZE + SPACE_XS)
        self.content_layout.addWidget(logo)

        name = TitleLabel(app_name, self)
        name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        name.setWordWrap(True)
        self.content_layout.addWidget(name)

        if version:
            version_label = CaptionLabel(f"Version {version}", self)
            version_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.content_layout.addWidget(version_label)

        self.content_layout.addSpacing(SPACE_S)

        if description:
            body = BodyLabel(description.replace("\n", " ").strip(), self)
            body.setWordWrap(True)
            body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            self.content_layout.addWidget(body)
            self.content_layout.addSpacing(SPACE_L)

        if author:
            self._add_meta_row("Author", author)
        if license_text:
            self._add_meta_row("License", license_text)
        if github:
            self.content_layout.addWidget(StrongBodyLabel("GitHub", self))
            link = FluentHyperlinkLabel(github, github, self)
            link.setWordWrap(True)
            self.content_layout.addWidget(link)

        copy_button = FluentPushButton("Copy", self._body.footer, icon="copy")
        copy_button.clicked.connect(self._copy_to_clipboard)
        self._body.footer.row.insertWidget(0, copy_button, 1)
```

</details>

### ⚙️ Method `clipboard_text`

```python
def clipboard_text(self) -> str
```

Return the plain-text About block used for Copy.

<details>
<summary>Code:</summary>

```python
def clipboard_text(self) -> str:
        return self._clipboard_text
```

</details>
