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
  - [⚙️ Method `set_long_press_actions`](#%EF%B8%8F-method-set_long_press_actions)
  - [⚙️ Method `unregister_all`](#%EF%B8%8F-method-unregister_all)
- [🔧 Function `hotkey_string_from_event`](#-function-hotkey_string_from_event)
- [🔧 Function `is_virtual_key_down`](#-function-is_virtual_key_down)
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
    action_long_press = Signal(str)
    registration_failed = Signal(str)

    def __init__(self, app: QApplication, parent: QObject | None = None) -> None:
        """Create a global hotkey manager bound to `app`."""
        super().__init__(parent)
        self._app = app
        self._hwnd_holder = QWidget()
        self._hwnd_holder.setWindowFlags(Qt.WindowType.Tool)
        self._hwnd_holder.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, on=True)
        self._id_to_action: dict[int, str] = {}
        self._id_to_vk: dict[int, int] = {}
        self._registered: list[ActionHotkeyBinding] = []
        self._long_press_actions: set[str] = set()
        self._long_press_ms = 450
        self._hold_action: str | None = None
        self._hold_vk = 0
        self._hold_long_fired = False
        self._hold_clock = QElapsedTimer()
        self._hold_poll = QTimer(self)
        self._hold_poll.setInterval(_HOLD_POLL_MS)
        self._hold_poll.timeout.connect(self._on_hold_poll)
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

    def set_long_press_actions(self, actions: Collection[str], *, hold_ms: int = 450) -> None:
        """Treat presses of these actions as short/long based on how long the key stays down."""
        self._long_press_actions = {name.strip() for name in actions if str(name).strip()}
        self._long_press_ms = max(100, int(hold_ms))

    def unregister_all(self) -> None:
        """Unregister all global hotkeys."""
        self._cancel_hold()
        if sys.platform != "win32" or not self._id_to_action:
            self._id_to_action.clear()
            self._id_to_vk.clear()
            self._registered.clear()
            return

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        for hotkey_id in list(self._id_to_action):
            user32.UnregisterHotKey(hwnd, hotkey_id)
        self._id_to_action.clear()
        self._id_to_vk.clear()
        self._registered.clear()

    def _begin_hold(self, action: str, vk: int) -> None:
        self._cancel_hold()
        self._hold_action = action
        self._hold_vk = vk
        self._hold_long_fired = False
        self._hold_clock.restart()
        self._hold_poll.start()

    def _cancel_hold(self) -> None:
        self._hold_poll.stop()
        self._hold_action = None
        self._hold_vk = 0
        self._hold_long_fired = False

    def _emit_action(self, action: str) -> None:
        self.action_triggered.emit(action)

    def _emit_long_press(self, action: str) -> None:
        self.action_long_press.emit(action)

    def _on_hold_poll(self) -> None:
        action = self._hold_action
        if action is None:
            self._hold_poll.stop()
            return

        key_down = is_virtual_key_down(self._hold_vk)
        if not key_down:
            self._hold_poll.stop()
            held_action = action
            long_fired = self._hold_long_fired
            self._cancel_hold()
            if not long_fired:
                self._emit_action(held_action)
            return

        if not self._hold_long_fired and self._hold_clock.elapsed() >= self._long_press_ms:
            self._hold_long_fired = True
            self._hold_poll.stop()
            held_action = action
            self._cancel_hold()
            self._emit_long_press(held_action)

    def _on_native_hotkey(self, hotkey_id: int) -> None:
        action = self._id_to_action.get(hotkey_id)
        if not action:
            return
        # Never run actions inside nativeEventFilter: modal UI / processEvents
        # re-enters Qt and PySide can report override errors (e.g. after a
        # screenshot toast with message text leaking into the failure string).
        vk = self._id_to_vk.get(hotkey_id, 0)
        if action in self._long_press_actions and vk:
            QTimer.singleShot(0, lambda name=action, key=vk: self._begin_hold(name, key))
            return
        QTimer.singleShot(0, lambda name=action: self._emit_action(name))

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
        self._id_to_vk[hotkey_id] = vk
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
        self._id_to_vk: dict[int, int] = {}
        self._registered: list[ActionHotkeyBinding] = []
        self._long_press_actions: set[str] = set()
        self._long_press_ms = 450
        self._hold_action: str | None = None
        self._hold_vk = 0
        self._hold_long_fired = False
        self._hold_clock = QElapsedTimer()
        self._hold_poll = QTimer(self)
        self._hold_poll.setInterval(_HOLD_POLL_MS)
        self._hold_poll.timeout.connect(self._on_hold_poll)
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

### ⚙️ Method `set_long_press_actions`

```python
def set_long_press_actions(self, actions: Collection[str], *, hold_ms: int = 450) -> None
```

Treat presses of these actions as short/long based on how long the key stays down.

<details>
<summary>Code:</summary>

```python
def set_long_press_actions(self, actions: Collection[str], *, hold_ms: int = 450) -> None:
        self._long_press_actions = {name.strip() for name in actions if str(name).strip()}
        self._long_press_ms = max(100, int(hold_ms))
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
        self._cancel_hold()
        if sys.platform != "win32" or not self._id_to_action:
            self._id_to_action.clear()
            self._id_to_vk.clear()
            self._registered.clear()
            return

        hwnd = int(self._hwnd_holder.winId())
        user32 = ctypes.windll.user32
        for hotkey_id in list(self._id_to_action):
            user32.UnregisterHotKey(hwnd, hotkey_id)
        self._id_to_action.clear()
        self._id_to_vk.clear()
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

## 🔧 Function `is_virtual_key_down`

```python
def is_virtual_key_down(vk: int) -> bool
```

Return whether a Win32 virtual-key code is currently held down.

<details>
<summary>Code:</summary>

```python
def is_virtual_key_down(vk: int) -> bool:
    if sys.platform != "win32" or vk <= 0:
        return False
    return bool(ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000)
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
