"""Global hotkey registration on Windows (RegisterHotKey + Qt native event filter)."""

from __future__ import annotations

import ctypes
import logging
import sys
from ctypes import wintypes
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import QAbstractNativeEventFilter, QByteArray, QKeyCombination, QObject, Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QWidget

if TYPE_CHECKING:
    from collections.abc import Callable

    from harrix_swiss_knife.action_hotkeys import ActionHotkeyBinding

logger = logging.getLogger(__name__)

HOTKEY_ID_BASE = 0x48534B  # 'HSK'
WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

_QT_MOD_TO_WIN32: dict[Qt.KeyboardModifier, int] = {
    Qt.KeyboardModifier.AltModifier: MOD_ALT,
    Qt.KeyboardModifier.ControlModifier: MOD_CONTROL,
    Qt.KeyboardModifier.ShiftModifier: MOD_SHIFT,
    Qt.KeyboardModifier.MetaModifier: MOD_WIN,
}

_QT_KEY_TO_VK: dict[Qt.Key, int] = {
    Qt.Key.Key_Backspace: 0x08,
    Qt.Key.Key_Tab: 0x09,
    Qt.Key.Key_Return: 0x0D,
    Qt.Key.Key_Escape: 0x1B,
    Qt.Key.Key_Space: 0x20,
    Qt.Key.Key_PageUp: 0x21,
    Qt.Key.Key_PageDown: 0x22,
    Qt.Key.Key_End: 0x23,
    Qt.Key.Key_Home: 0x24,
    Qt.Key.Key_Left: 0x25,
    Qt.Key.Key_Up: 0x26,
    Qt.Key.Key_Right: 0x27,
    Qt.Key.Key_Down: 0x28,
    Qt.Key.Key_Delete: 0x2E,
    Qt.Key.Key_F1: 0x70,
    Qt.Key.Key_F2: 0x71,
    Qt.Key.Key_F3: 0x72,
    Qt.Key.Key_F4: 0x73,
    Qt.Key.Key_F5: 0x74,
    Qt.Key.Key_F6: 0x75,
    Qt.Key.Key_F7: 0x76,
    Qt.Key.Key_F8: 0x77,
    Qt.Key.Key_F9: 0x78,
    Qt.Key.Key_F10: 0x79,
    Qt.Key.Key_F11: 0x7A,
    Qt.Key.Key_F12: 0x7B,
}


class GlobalHotkeyManager(QObject):
    """Register multiple global hotkeys while the Qt application is running (Windows only)."""

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


class _HotkeyNativeEventFilter(QAbstractNativeEventFilter):
    def __init__(self, on_hotkey: Callable[[int], None]) -> None:
        super().__init__()
        self._on_hotkey = on_hotkey

    def nativeEventFilter(  # noqa: N802
        self,
        event_type: QByteArray | bytes | bytearray | memoryview,
        message: int,
    ) -> tuple[bool, int]:
        try:
            return self._filter_native_event(event_type, message)
        except KeyboardInterrupt:
            app = QApplication.instance()
            if app is not None:
                app.quit()
            return False, 0

    def _filter_native_event(
        self,
        event_type: QByteArray | bytes | bytearray | memoryview,
        message: int,
    ) -> tuple[bool, int]:
        if sys.platform != "win32" or _event_type_to_bytes(event_type) != b"windows_generic_MSG":
            return False, 0

        msg = wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY:
            self._on_hotkey(int(msg.wParam))
            return True, 0
        return False, 0


def hotkey_string_from_event(key: int, modifiers: Qt.KeyboardModifier) -> str:
    """Build portable hotkey text from a key event."""
    combination = QKeyCombination(modifiers, Qt.Key(key))
    return QKeySequence(combination).toString(QKeySequence.SequenceFormat.PortableText)


def parse_hotkey_string(hotkey_str: str) -> tuple[int, int]:
    """Parse portable hotkey text into Win32 modifiers and virtual-key code."""
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


def _event_type_to_bytes(event_type: QByteArray | bytes | bytearray | memoryview) -> bytes:
    if isinstance(event_type, QByteArray):
        return bytes(event_type.data())
    return bytes(event_type)
