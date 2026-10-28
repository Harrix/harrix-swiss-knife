---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `gallery.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `build_gallery`](#-function-build_gallery)
- [🔧 Function `main`](#-function-main)

</details>

## 🔧 Function `build_gallery`

```python
def build_gallery() -> fw.FluentNavigationWindow
```

Build the gallery window with one page per widget category.

<details>
<summary>Code:</summary>

```python
def build_gallery() -> fw.FluentNavigationWindow:
    _SHOWCASE_COUNTS.clear()
    theme_button = fw.FluentIconButton("sun" if FluentTheme.instance().is_dark() else "moon", tooltip="Toggle theme")
    window = fw.FluentNavigationWindow("Fluent gallery", install_caption=False)
    _install_main_menu(window, theme_button)
    window.install_caption(trailing_widgets=[theme_button])
    theme_button.clicked.connect(lambda: _toggle_gallery_theme(theme_button))
    window.resize(*_GALLERY_SIZE)
    pages = (
        ("basic", "Basic input", "mouse-pointer-click", _basic_page()),
        ("text", "Text and selection", "text-cursor-input", _text_page()),
        ("display", "Status and info", "info", _display_page()),
        ("cards", "Cards", "layout-grid", _cards_page()),
        ("navigation", "Navigation", "navigation", _navigation_page()),
        ("views", "Collections", "list", _views_page()),
        ("dialogs", "Dialogs and flyouts", "message-square", _dialogs_page(window)),
        ("pickers", "Date and time", "calendar", _pickers_page()),
        ("editors", "Editors", "code", _editors_page()),
    )
    for key, text, icon, page in pages:
        window.add_page(key, text, page, icon=icon)
    _register_showcase(theme_button, "themeToggleButton")
    return window
```

</details>

## 🔧 Function `main`

```python
def main() -> int
```

Show the gallery.

<details>
<summary>Code:</summary>

```python
def main() -> int:
    existing = QApplication.instance()
    app = existing if isinstance(existing, QApplication) else QApplication(sys.argv)
    install_app_fonts(app)
    FluentTheme.instance().load_from_config()
    window = build_gallery()
    window.show()
    return app.exec()
```

</details>
