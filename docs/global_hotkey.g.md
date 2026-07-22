---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `global_hotkey.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `GlobalHotkeyManager`](#%EF%B8%8F-class-globalhotkeymanager)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `register`](#%EF%B8%8F-method-register)
  - [⚙️ Method `register_from_config`](#%EF%B8%8F-method-register_from_config)
  - [⚙️ Method `registered_hotkey`](#%EF%B8%8F-method-registered_hotkey)
  - [⚙️ Method `unregister`](#%EF%B8%8F-method-unregister)
- [🔧 Function `hotkey_string_from_event`](#-function-hotkey_string_from_event)
- [🔧 Function `parse_hotkey_string`](#-function-parse_hotkey_string)

</details>

## 🏛️ Class `GlobalHotkeyManager`

```python
class GlobalHotkeyManager(QObject)
```

Register a global hotkey while the Qt application is running (Windows only).

<details>
<summary>Code:</summary>

```python
class GlobalHotkeyManager(QObject):

    hotkey_triggered = Signal()
    registration_failed = Signal(str)

    def __init__(self, app: QApplication, parent: QObject | None = None) -> None:
        """Create a global hotkey manager bound to `app`."""
        super().__init__(parent)
        self._app = app
        self._hwnd_holder = QWidget()
        self._hwnd_holder.setWindowFlags(Qt.WindowType.Tool)
        self._hwnd_holder.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        self._filter = _HotkeyNativeEventFilter(self.hotkey_triggered.emit)
        self._app.installNativeEventFilter(self._filter)
        self._registered_hotkey = ""

    def register(self, hotkey_str: str) -> bool:
        """Register `hotkey_str` globally. Returns `False` if registration failed."""
        if sys.platform != "win32":
            logger.info("Global hotkeys are supported on Windows only.")
            return False

        text = hotkey_str.strip()
        if not text:
            self.unregister()
            return False

        self.unregister()
        try:
            modifiers, vk = parse_hotkey_string(text)
        except ValueError as exc:
            self.registration_failed.emit(str(exc))
            return False

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        ok = bool(user32.RegisterHotKey(hwnd, HOTKEY_ID, modifiers | MOD_NOREPEAT, vk))
        if not ok:
            self.registration_failed.emit(
                f"Could not register hotkey {text!r}. It may already be used by another application.",
            )
            return False

        self._registered_hotkey = text
        logger.info("Registered quick launcher hotkey: %s", text)
        return True

    def register_from_config(self, _config: dict[str, Any] | None = None) -> bool:
        """Register hotkey from `config-temp.json` if set."""
        hotkey = load_quick_launcher_hotkey()
        if not hotkey:
            return False
        return self.register(hotkey)

    @property
    def registered_hotkey(self) -> str:
        """Currently registered hotkey string, or empty if none."""
        return self._registered_hotkey

    def unregister(self) -> None:
        """Unregister the current global hotkey."""
        if sys.platform != "win32" or not self._registered_hotkey:
            self._registered_hotkey = ""
            return

        hwnd = int(self._hwnd_holder.winId())
        ctypes.windll.user32.UnregisterHotKey(hwnd, HOTKEY_ID)
        self._registered_hotkey = ""
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, app: QApplication, parent: QObject | None = None) -> None
```

Create a global hotkey manager bound to `app`.

<details>
<summary>Code:</summary>

```python
def __init__(self, app: QApplication, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._app = app
        self._hwnd_holder = QWidget()
        self._hwnd_holder.setWindowFlags(Qt.WindowType.Tool)
        self._hwnd_holder.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        self._filter = _HotkeyNativeEventFilter(self.hotkey_triggered.emit)
        self._app.installNativeEventFilter(self._filter)
        self._registered_hotkey = ""
```

</details>

### ⚙️ Method `register`

```python
def register(self, hotkey_str: str) -> bool
```

Register `hotkey_str` globally. Returns `False` if registration failed.

<details>
<summary>Code:</summary>

```python
def register(self, hotkey_str: str) -> bool:
        if sys.platform != "win32":
            logger.info("Global hotkeys are supported on Windows only.")
            return False

        text = hotkey_str.strip()
        if not text:
            self.unregister()
            return False

        self.unregister()
        try:
            modifiers, vk = parse_hotkey_string(text)
        except ValueError as exc:
            self.registration_failed.emit(str(exc))
            return False

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        ok = bool(user32.RegisterHotKey(hwnd, HOTKEY_ID, modifiers | MOD_NOREPEAT, vk))
        if not ok:
            self.registration_failed.emit(
                f"Could not register hotkey {text!r}. It may already be used by another application.",
            )
            return False

        self._registered_hotkey = text
        logger.info("Registered quick launcher hotkey: %s", text)
        return True
```

</details>

### ⚙️ Method `register_from_config`

```python
def register_from_config(self, _config: dict[str, Any] | None = None) -> bool
```

Register hotkey from `config-temp.json` if set.

<details>
<summary>Code:</summary>

```python
def register_from_config(self, _config: dict[str, Any] | None = None) -> bool:
        hotkey = load_quick_launcher_hotkey()
        if not hotkey:
            return False
        return self.register(hotkey)
```

</details>

### ⚙️ Method `registered_hotkey`

```python
def registered_hotkey(self) -> str
```

Currently registered hotkey string, or empty if none.

<details>
<summary>Code:</summary>

```python
def registered_hotkey(self) -> str:
        return self._registered_hotkey
```

</details>

### ⚙️ Method `unregister`

```python
def unregister(self) -> None
```

Unregister the current global hotkey.

<details>
<summary>Code:</summary>

```python
def unregister(self) -> None:
        if sys.platform != "win32" or not self._registered_hotkey:
            self._registered_hotkey = ""
            return

        hwnd = int(self._hwnd_holder.winId())
        ctypes.windll.user32.UnregisterHotKey(hwnd, HOTKEY_ID)
        self._registered_hotkey = ""
```

</details>

## 🔧 Function `hotkey_string_from_event`

```python
def hotkey_string_from_event(key: int, modifiers: Qt.KeyboardModifier) -> str
```

Build portable hotkey text from a key event.

<details>
<summary>Code:</summary>

```python
def hotkey_string_from_event(key: int, modifiers: Qt.KeyboardModifier) -> str:
    combination = QKeyCombination(modifiers, Qt.Key(key))
    return QKeySequence(combination).toString(QKeySequence.SequenceFormat.PortableText)
```

</details>

## 🔧 Function `parse_hotkey_string`

```python
def parse_hotkey_string(hotkey_str: str) -> tuple[int, int]
```

Parse portable hotkey text into Win32 modifiers and virtual-key code.

<details>
<summary>Code:</summary>

```python
def parse_hotkey_string(hotkey_str: str) -> tuple[int, int]:
    text = hotkey_str.strip()
    if not text:
        msg = "Hotkey string is empty."
        raise ValueError(msg)

    sequence = QKeySequence.fromString(text, QKeySequence.SequenceFormat.PortableText)
    if sequence.isEmpty():
        msg = f"Invalid hotkey: {hotkey_str!r}"
        raise ValueError(msg)

    # QKeySequence supports [] at runtime; stubs omit __getitem__.
    combination = cast("Any", sequence)[0]
    if not isinstance(combination, QKeyCombination):
        msg = f"Invalid hotkey: {hotkey_str!r}"
        raise TypeError(msg)

    modifiers = 0
    qt_modifiers = combination.keyboardModifiers()
    for qt_mod, win_mod in _QT_MOD_TO_WIN32.items():
        if qt_modifiers & qt_mod:
            modifiers |= win_mod

    key = combination.key()
    if key in _QT_KEY_TO_VK:
        return modifiers, _QT_KEY_TO_VK[key]

    key_name = QKeySequence(key).toString(QKeySequence.SequenceFormat.PortableText)
    if len(key_name) == 1 and key_name.isalnum():
        return modifiers, ord(key_name.upper())

    msg = f"Unsupported hotkey key: {hotkey_str!r}"
    raise ValueError(msg)
```

</details>
