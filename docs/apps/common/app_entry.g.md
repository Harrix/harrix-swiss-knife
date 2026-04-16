---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `app_entry.py`

## 🔧 Function `run_app_main`

```python
def run_app_main(main_window_factory: Callable[[], QMainWindow]) -> None
```

Run the standard app main loop.

Args:

- `main_window_factory` (`Callable[[], QMainWindow]`): Callable that
  returns a new `QMainWindow` instance (typically the `MainWindow` class).
- `icon_path` (`str`): Resource path for the app icon.
  Defaults to `":/assets/logo.svg"`.
- `set_tab_index_zero` (`bool`): Whether to select tab index 0 on the
  created window when it exposes a `tabWidget` attribute.
  Defaults to `True`.

<details>
<summary>Code:</summary>

```python
def run_app_main(
    main_window_factory: Callable[[], QMainWindow],
    *,
    icon_path: str = ":/assets/logo.svg",
    set_tab_index_zero: bool = True,
) -> None:
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    try:
        win = main_window_factory()
    except Exception as exc:  # noqa: BLE001
        message_box.critical(None, "Error", str(exc))
        sys.exit(1)
    if set_tab_index_zero:
        tab_widget = getattr(win, "tabWidget", None)
        if tab_widget is not None:
            tab_widget.setCurrentIndex(0)
    sys.exit(app.exec())
```

</details>
