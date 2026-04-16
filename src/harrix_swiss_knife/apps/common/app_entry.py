"""Shared `__main__` helper for app entry points.

Provides `run_app_main`, a thin wrapper around the boilerplate that existed in
each app's `__main__` block:

```python
app = QApplication(sys.argv)
app.setWindowIcon(QIcon(":/assets/logo.svg"))
try:
    win = MainWindow()
except Exception as exc:
    message_box.critical(None, "Error", str(exc))
    sys.exit(1)
else:
    win.tabWidget.setCurrentIndex(0)
    sys.exit(app.exec())
```
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from harrix_swiss_knife.apps.common import message_box

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QMainWindow


def run_app_main(
    main_window_factory: Callable[[], QMainWindow],
    *,
    icon_path: str = ":/assets/logo.svg",
    set_tab_index_zero: bool = True,
) -> None:
    """Run the standard app main loop.

    Args:

    - `main_window_factory` (`Callable[[], QMainWindow]`): Callable that
      returns a new `QMainWindow` instance (typically the `MainWindow` class).
    - `icon_path` (`str`): Resource path for the app icon.
      Defaults to `":/assets/logo.svg"`.
    - `set_tab_index_zero` (`bool`): Whether to select tab index 0 on the
      created window when it exposes a `tabWidget` attribute.
      Defaults to `True`.

    """
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path))
    try:
        win = main_window_factory()
    except Exception as exc:
        message_box.critical(None, "Error", str(exc))
        sys.exit(1)
    if set_tab_index_zero:
        tab_widget = getattr(win, "tabWidget", None)
        if tab_widget is not None:
            tab_widget.setCurrentIndex(0)
    sys.exit(app.exec())
