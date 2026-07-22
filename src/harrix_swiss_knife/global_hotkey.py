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

from harrix_swiss_knife.actions.quick_launcher.hotkey import load_quick_launcher_hotkey

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

HOTKEY_ID = 0x48534B  # 'HSK'
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
    """Register a global hotkey while the Qt application is running (Windows only)."""

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


class _HotkeyNativeEventFilter(QAbstractNativeEventFilter):
    def __init__(self, on_hotkey: Callable[[], None]) -> None:
        super().__init__()
        self._on_hotkey = on_hotkey

    def nativeEventFilter(  # noqa: N802
        self,
        event_type: QByteArray | bytes | bytearray | memoryview,
        message: int,
    ) -> tuple[bool, int]:
        if sys.platform != "win32" or _event_type_to_bytes(event_type) != b"windows_generic_MSG":
            return False, 0

        msg = wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
            self._on_hotkey()
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
