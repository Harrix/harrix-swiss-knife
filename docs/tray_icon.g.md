---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `tray_icon.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `TrayIcon`](#%EF%B8%8F-class-trayicon)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `ensure_main_window`](#%EF%B8%8F-method-ensure_main_window)
  - [⚙️ Method `on_activated`](#%EF%B8%8F-method-on_activated)

</details>

## 🏛️ Class `TrayIcon`

```python
class TrayIcon(QSystemTrayIcon)
```

Represent a system tray icon with an associated context menu and main window.

Attributes:

- `main_window` (`main_window.MainWindow | None`):
  The main window associated with the tray icon. Defaults to `None`.
- `menu` (`QMenu`):
  The context menu displayed when interacting with the tray icon.

<details>
<summary>Code:</summary>

```python
class TrayIcon(QSystemTrayIcon):

    def __init__(
        self,
        icon: QIcon,
        menu: QMenu,
        parent: QWidget | None = None,
        *,
        output_bus: ActionOutputBus | None = None,
    ) -> None:
        """Initialize the `TrayIcon` with the given icon and menu.

        Args:

        - `icon` (`QIcon`):
          The icon to display in the system tray.
        - `menu` (`QMenu`):
          The context menu to associate with the tray icon.
        - `parent` (`QWidget | None`):
          The parent widget. Defaults to `None`.

        Sets up the system tray icon, context menu, and connects the activation signal
        to handle user interactions.

        """
        super().__init__(icon, parent)
        set_menu_tooltips_visible_recursive(menu)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window: main_window.MainWindow | None = None
        self.menu: QMenu = menu
        self._output_bus = output_bus

    def ensure_main_window(self) -> main_window.MainWindow:
        """Create the main window on first use."""
        if self.main_window is None:
            self.main_window = main_window.MainWindow(self.menu, output_bus=self._output_bus)
        return self.main_window

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle the activation event of the system tray icon.

        Args:

        - `reason` (`QSystemTrayIcon.ActivationReason`):
          The reason for the activation event.

        If the tray icon is clicked (Trigger), it shows and brings the main window to the front.

        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            window = self.ensure_main_window()
            window.show()
            window.raise_()
            window.activateWindow()
            window.focus_initial_input()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, icon: QIcon, menu: QMenu, parent: QWidget | None = None) -> None
```

Initialize the `TrayIcon` with the given icon and menu.

Args:

- `icon` (`QIcon`):
  The icon to display in the system tray.
- `menu` (`QMenu`):
  The context menu to associate with the tray icon.
- `parent` (`QWidget | None`):
  The parent widget. Defaults to `None`.

Sets up the system tray icon, context menu, and connects the activation signal
to handle user interactions.

<details>
<summary>Code:</summary>

```python
def __init__(
        self,
        icon: QIcon,
        menu: QMenu,
        parent: QWidget | None = None,
        *,
        output_bus: ActionOutputBus | None = None,
    ) -> None:
        super().__init__(icon, parent)
        set_menu_tooltips_visible_recursive(menu)
        self.setContextMenu(menu)
        self.activated.connect(self.on_activated)
        self.main_window: main_window.MainWindow | None = None
        self.menu: QMenu = menu
        self._output_bus = output_bus
```

</details>

### ⚙️ Method `ensure_main_window`

```python
def ensure_main_window(self) -> main_window.MainWindow
```

Create the main window on first use.

<details>
<summary>Code:</summary>

```python
def ensure_main_window(self) -> main_window.MainWindow:
        if self.main_window is None:
            self.main_window = main_window.MainWindow(self.menu, output_bus=self._output_bus)
        return self.main_window
```

</details>

### ⚙️ Method `on_activated`

```python
def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None
```

Handle the activation event of the system tray icon.

Args:

- `reason` (`QSystemTrayIcon.ActivationReason`):
  The reason for the activation event.

If the tray icon is clicked (Trigger), it shows and brings the main window to the front.

<details>
<summary>Code:</summary>

```python
def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            window = self.ensure_main_window()
            window.show()
            window.raise_()
            window.activateWindow()
            window.focus_initial_input()
```

</details>
