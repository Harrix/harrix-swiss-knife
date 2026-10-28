---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `fluent_gallery.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnFluentGallery`](#%EF%B8%8F-class-onfluentgallery)
  - [⚙️ Method `clear_gallery_window (classmethod)`](#%EF%B8%8F-method-clear_gallery_window-classmethod)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnFluentGallery`

```python
class OnFluentGallery(ActionBase)
```

Open a stand-alone window with every Fluent widget and copy-name menus.

<details>
<summary>Code:</summary>

```python
class OnFluentGallery(ActionBase):

    icon = "🧩"
    title = "Fluent widget gallery"
    gallery_window: ClassVar[QWidget | None] = None

    @classmethod
    def clear_gallery_window(cls, *_args: object) -> None:
        """Drop the cached gallery window after Qt destroys it."""
        cls.gallery_window = None

    @ActionBase.handle_exceptions("fluent gallery")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show the Fluent gallery, reusing the existing window when still valid."""
        window = OnFluentGallery.gallery_window
        if window is not None and isValid(window):
            window.show()
            window.raise_()
            window.activateWindow()
            self.add_line("✅ Fluent widget gallery is already open")
            return

        from harrix_swiss_knife.fluent.gallery import build_gallery  # noqa: PLC0415
        from harrix_swiss_knife.fluent.theme import FluentTheme  # noqa: PLC0415

        FluentTheme.instance().load_from_config()
        window = build_gallery()
        window.destroyed.connect(OnFluentGallery.clear_gallery_window)
        OnFluentGallery.gallery_window = window
        window.show()
        window.raise_()
        window.activateWindow()
        self.add_line("✅ Fluent widget gallery opened")
```

</details>

### ⚙️ Method `clear_gallery_window (classmethod)`

```python
def clear_gallery_window(cls, *_args: object) -> None
```

Drop the cached gallery window after Qt destroys it.

<details>
<summary>Code:</summary>

```python
def clear_gallery_window(cls, *_args: object) -> None:
        cls.gallery_window = None
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Show the Fluent gallery, reusing the existing window when still valid.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        window = OnFluentGallery.gallery_window
        if window is not None and isValid(window):
            window.show()
            window.raise_()
            window.activateWindow()
            self.add_line("✅ Fluent widget gallery is already open")
            return

        from harrix_swiss_knife.fluent.gallery import build_gallery  # noqa: PLC0415
        from harrix_swiss_knife.fluent.theme import FluentTheme  # noqa: PLC0415

        FluentTheme.instance().load_from_config()
        window = build_gallery()
        window.destroyed.connect(OnFluentGallery.clear_gallery_window)
        OnFluentGallery.gallery_window = window
        window.show()
        window.raise_()
        window.activateWindow()
        self.add_line("✅ Fluent widget gallery opened")
```

</details>
