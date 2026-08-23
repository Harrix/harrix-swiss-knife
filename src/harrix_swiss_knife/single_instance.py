"""Ensure only one Harrix Swiss Knife tray process runs per user.

A second launch connects to the first process over a local socket and asks it
to show the command-cards window, then exits.
"""

from __future__ import annotations

import getpass
import logging
import os
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

_ACTIVATE_MESSAGE = b"show\n"
_CONNECT_TIMEOUT_MS = 250
_WRITE_TIMEOUT_MS = 250

_held: SingleInstance | None = None


class SingleInstance(QObject):
    """Listen for (or notify) another tray process on a per-user local socket."""

    activate_requested = Signal()

    def __init__(self, name: str | None = None, parent: QObject | None = None) -> None:
        """Create a guard for `name` (defaults to a per-user Swiss Knife socket)."""
        super().__init__(parent)
        self._name = name or default_server_name()
        self._server: QLocalServer | None = None

    @property
    def name(self) -> str:
        """Return the local-socket name this guard uses."""
        return self._name

    def release(self) -> None:
        """Close the listener so another process can become primary."""
        server = self._server
        self._server = None
        if server is None:
            return
        server.close()
        QLocalServer.removeServer(self._name)

    def try_claim(self) -> bool:
        """Become the primary instance, or notify the existing one.

        Returns:

        - `bool`: `True` when this process should keep running. `False` when
          another instance is already running and was asked to show the window.

        """
        if _notify_existing(self._name):
            return False
        QLocalServer.removeServer(self._name)
        server = QLocalServer(self)
        server.newConnection.connect(self._on_new_connection)
        if server.listen(self._name):
            self._server = server
            return True
        server.deleteLater()
        # Another process won the listen race — ask it to show the window.
        if _notify_existing(self._name):
            return False
        logger.warning("Could not listen on %s and no peer accepted a connection", self._name)
        return True

    def _on_new_connection(self) -> None:
        server = self._server
        if server is None:
            return
        socket = server.nextPendingConnection()
        if socket is None:
            return

        def _read() -> None:
            payload = bytes(socket.readAll())
            if _ACTIVATE_MESSAGE.strip() in payload:
                self.activate_requested.emit()
            socket.disconnectFromServer()

        socket.readyRead.connect(_read)
        if socket.bytesAvailable():
            _read()


def acquire_tray_instance(on_activate: Callable[[], None], *, name: str | None = None) -> SingleInstance | None:
    """Claim the tray singleton. Return the guard, or `None` when another instance owns it."""
    global _held  # noqa: PLW0603
    instance = SingleInstance(name=name)
    instance.activate_requested.connect(on_activate)
    if not instance.try_claim():
        instance.deleteLater()
        return None
    _held = instance
    return instance


def default_server_name() -> str:
    """Return a per-user local-socket name for the tray app."""
    raw = os.environ.get("USERNAME") or os.environ.get("USER") or getpass.getuser()
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in raw)
    return f"harrix-swiss-knife-{safe or 'user'}"


def release_held_instance() -> None:
    """Release the process-wide tray singleton (used before restart)."""
    global _held  # noqa: PLW0603
    if _held is None:
        return
    _held.release()
    _held = None


def _notify_existing(name: str) -> bool:
    """Ask a listening instance to show the command window. Return whether it accepted."""
    socket = QLocalSocket()
    socket.connectToServer(name)
    if not socket.waitForConnected(_CONNECT_TIMEOUT_MS):
        socket.deleteLater()
        return False
    socket.write(_ACTIVATE_MESSAGE)
    socket.flush()
    socket.waitForBytesWritten(_WRITE_TIMEOUT_MS)
    socket.disconnectFromServer()
    if socket.state() != QLocalSocket.LocalSocketState.UnconnectedState:
        socket.waitForDisconnected(_WRITE_TIMEOUT_MS)
    socket.deleteLater()
    return True
