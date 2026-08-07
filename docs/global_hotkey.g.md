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
  - [⚙️ Method `register_all`](#%EF%B8%8F-method-register_all)
  - [⚙️ Method `registered_bindings (property)`](#%EF%B8%8F-method-registered_bindings-property)
  - [⚙️ Method `unregister_all`](#%EF%B8%8F-method-unregister_all)
- [🔧 Function `hotkey_string_from_event`](#-function-hotkey_string_from_event)
- [🔧 Function `parse_hotkey_string`](#-function-parse_hotkey_string)

</details>

## 🏛️ Class `GlobalHotkeyManager`

```python
class GlobalHotkeyManager(QObject)
```

Register multiple global hotkeys while the Qt application is running (Windows only).

<details>
<summary>Code:</summary>

```python
class GlobalHotkeyManager(QObject):

    action_triggered = Signal(str)
    registration_failed = Signal(str)

    def __init__(self, app: QApplication, parent: QObject | None = None) -> None:
        """Create a global hotkey manager bound to `app`."""
        super().__init__(parent)
        self._app = app
        self._hwnd_holder = QWidget()
        self._hwnd_holder.setWindowFlags(Qt.WindowType.Tool)
        self._hwnd_holder.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        self._id_to_action: dict[int, str] = {}
        self._registered: list[ActionHotkeyBinding] = []
        self._filter = _HotkeyNativeEventFilter(self._on_native_hotkey)
        self._app.installNativeEventFilter(self._filter)

    def register_all(self, bindings: list[ActionHotkeyBinding]) -> int:
        """Register all bindings. Returns the number of successfully registered hotkeys."""
        if sys.platform != "win32":
            logger.info("Global hotkeys are supported on Windows only.")
            return 0

        self.unregister_all()
        registered_count = 0
        for index, binding in enumerate(bindings):
            if self._register_one(HOTKEY_ID_BASE + index, binding):
                registered_count += 1
        return registered_count

    @property
    def registered_bindings(self) -> list[ActionHotkeyBinding]:
        """Currently registered bindings."""
        return list(self._registered)

    def unregister_all(self) -> None:
        """Unregister all global hotkeys."""
        if sys.platform != "win32" or not self._id_to_action:
            self._id_to_action.clear()
            self._registered.clear()
            return

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        for hotkey_id in list(self._id_to_action):
            user32.UnregisterHotKey(hwnd, hotkey_id)
        self._id_to_action.clear()
        self._registered.clear()

    def _on_native_hotkey(self, hotkey_id: int) -> None:
        action = self._id_to_action.get(hotkey_id)
        if action:
            self.action_triggered.emit(action)

    def _register_one(self, hotkey_id: int, binding: ActionHotkeyBinding) -> bool:
        text = binding.hotkey.strip()
        if not text:
            return False

        try:
            modifiers, vk = parse_hotkey_string(text)
        except ValueError as exc:
            self.registration_failed.emit(str(exc))
            return False

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        ok = bool(user32.RegisterHotKey(hwnd, hotkey_id, modifiers | MOD_NOREPEAT, vk))
        if not ok:
            self.registration_failed.emit(
                f"Could not register hotkey {text!r} for {binding.action}. "
                "It may already be used by another application.",
            )
            return False

        self._id_to_action[hotkey_id] = binding.action
        self._registered.append(binding)
        logger.info("Registered hotkey %s -> %s", text, binding.action)
        return True
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
        self._id_to_action: dict[int, str] = {}
        self._registered: list[ActionHotkeyBinding] = []
        self._filter = _HotkeyNativeEventFilter(self._on_native_hotkey)
        self._app.installNativeEventFilter(self._filter)
```

</details>

### ⚙️ Method `register_all`

```python
def register_all(self, bindings: list[ActionHotkeyBinding]) -> int
```

Register all bindings. Returns the number of successfully registered hotkeys.

<details>
<summary>Code:</summary>

```python
def register_all(self, bindings: list[ActionHotkeyBinding]) -> int:
        if sys.platform != "win32":
            logger.info("Global hotkeys are supported on Windows only.")
            return 0

        self.unregister_all()
        registered_count = 0
        for index, binding in enumerate(bindings):
            if self._register_one(HOTKEY_ID_BASE + index, binding):
                registered_count += 1
        return registered_count
```

</details>

### ⚙️ Method `registered_bindings (property)`

```python
def registered_bindings(self) -> list[ActionHotkeyBinding]
```

Currently registered bindings.

<details>
<summary>Code:</summary>

```python
def registered_bindings(self) -> list[ActionHotkeyBinding]:
        return list(self._registered)
```

</details>

### ⚙️ Method `unregister_all`

```python
def unregister_all(self) -> None
```

Unregister all global hotkeys.

<details>
<summary>Code:</summary>

```python
def unregister_all(self) -> None:
        if sys.platform != "win32" or not self._id_to_action:
            self._id_to_action.clear()
            self._registered.clear()
            return

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        for hotkey_id in list(self._id_to_action):
            user32.UnregisterHotKey(hwnd, hotkey_id)
        self._id_to_action.clear()
        self._registered.clear()
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
