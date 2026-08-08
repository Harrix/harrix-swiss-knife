"""Configure LAN photo sync folder, port, and show phone connection status."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.photo_sync.lan import list_lan_ipv4
from harrix_swiss_knife.photo_sync.server import (
    DEFAULT_PORT,
    PhotoSyncServer,
    get_phone_connection_info,
    get_shared_server,
)


class OnPhotoSyncSettings(ActionBase):
    """Open Photo Sync settings: destination folder, port, and phone status.

    Edits `path_photos` and `photo_sync_port` in `config.json`. Shows whether the
    LAN listener is running and the last activity from a paired phone.

    """

    icon = "⚙️"
    title = "Photo sync settings"
    description = "Folder, port, and phone connection status for LAN Photo Sync"
    cli_available = False
    _dialog: ClassVar[QDialog | None] = None

    CONFIG_FOLDER_KEY = "path_photos"
    CONFIG_PORT_KEY = "photo_sync_port"
    _MAX_TCP_PORT = 65535
    _PHONE_ACTIVE_SECONDS = 45
    _SECONDS_PER_MINUTE = 60
    _DEVICE_ID_SHORT_LEN = 16
    _DEVICE_ID_PREFIX_LEN = 12

    @ActionBase.handle_exceptions("photo sync settings")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Show the Photo Sync settings dialog."""
        if OnPhotoSyncSettings._dialog is not None:
            OnPhotoSyncSettings._dialog.raise_()
            OnPhotoSyncSettings._dialog.activateWindow()
            return

        dialog = self._build_dialog()
        OnPhotoSyncSettings._dialog = dialog
        dialog.show()

    def _build_dialog(self) -> QDialog:
        dialog = QDialog()
        dialog.setWindowTitle("Photo sync — settings")
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)  # noqa: FBT003
        dialog.resize(560, 420)
        layout = QVBoxLayout(dialog)

        title = QLabel("Photo Sync settings")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        hint = QLabel(
            "New photos are saved into the folder root. Existing files are detected "
            "by content hash in all subfolders. Start listening with "
            "<b>Photo sync listen (LAN)</b>."
        )
        hint.setWordWrap(True)
        hint.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(hint)

        form = QFormLayout()
        folder_edit = QLineEdit((self.config.get(self.CONFIG_FOLDER_KEY) or "").strip())
        folder_row = QHBoxLayout()
        folder_row.addWidget(folder_edit, stretch=1)
        browse_btn = QPushButton("Browse…")
        folder_row.addWidget(browse_btn)
        form.addRow("Photos folder:", folder_row)

        port_spin = QSpinBox()
        port_spin.setRange(1, self._MAX_TCP_PORT)
        port_raw = self.config.get(self.CONFIG_PORT_KEY, DEFAULT_PORT)
        try:
            port_value = int(port_raw)
        except (TypeError, ValueError):
            port_value = DEFAULT_PORT
        if not (1 <= port_value <= self._MAX_TCP_PORT):
            port_value = DEFAULT_PORT
        port_spin.setValue(port_value)
        form.addRow("Listen port:", port_spin)
        layout.addLayout(form)

        status = QLabel()
        status.setWordWrap(True)
        status.setTextFormat(Qt.TextFormat.RichText)
        status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        status.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        status.setMinimumHeight(180)
        layout.addWidget(status, stretch=1)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        close_btn = QPushButton("Close")
        buttons.addWidget(save_btn)
        buttons.addStretch(1)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

        def browse() -> None:
            chosen = self.dialogs.get_existing_directory(
                "Select photos sync folder",
                folder_edit.text().strip() or str(Path.home()),
            )
            if chosen is not None:
                folder_edit.setText(str(chosen))

        def save() -> None:
            folder = folder_edit.text().strip().strip("\"'")
            if not folder:
                QMessageBox.warning(dialog, "Photo sync", "Photos folder cannot be empty.")
                return
            path = Path(folder).expanduser()
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    QMessageBox.warning(dialog, "Photo sync", f"Cannot create folder:\n{exc}")
                    return
            if not path.is_dir():
                QMessageBox.warning(dialog, "Photo sync", "Selected path is not a folder.")
                return

            resolved = str(path.resolve())
            port = int(port_spin.value())
            self._save_config_value(self.CONFIG_FOLDER_KEY, resolved)
            self._save_config_value(self.CONFIG_PORT_KEY, port)
            self.invalidate_config_cache()
            folder_edit.setText(resolved)
            self.add_line(f"Photo sync folder: {resolved}")
            self.add_line(f"Photo sync port: {port}")
            self.show_toast("Photo sync settings saved")

            server = get_shared_server()
            if server is not None and server.is_running:
                QMessageBox.information(
                    dialog,
                    "Photo sync",
                    "Settings saved.\n\n"
                    "The listener is still using the previous folder/port until you "
                    "stop and start Photo sync listen (LAN) again.",
                )
            refresh_status()

        def refresh_status() -> None:
            status.setText(self._status_html(folder_edit.text().strip(), int(port_spin.value())))

        timer = QTimer(dialog)
        timer.setInterval(1000)
        timer.timeout.connect(refresh_status)
        timer.start()
        refresh_status()

        browse_btn.clicked.connect(browse)
        save_btn.clicked.connect(save)
        close_btn.clicked.connect(dialog.close)

        def on_finished() -> None:
            timer.stop()
            if OnPhotoSyncSettings._dialog is dialog:
                OnPhotoSyncSettings._dialog = None

        dialog.finished.connect(on_finished)
        return dialog

    @classmethod
    def _format_age(cls, seconds: float) -> str:
        total = int(seconds)
        unit = cls._SECONDS_PER_MINUTE
        if total < unit:
            return f"{total}s"
        minutes, sec = divmod(total, unit)
        if minutes < unit:
            return f"{minutes}m {sec}s"
        hours, minutes = divmod(minutes, unit)
        return f"{hours}h {minutes}m"

    @staticmethod
    def _listener_mismatch_note(
        server: PhotoSyncServer,
        *,
        configured_folder: str,
        configured_port: int,
    ) -> str:
        reasons: list[str] = []
        if configured_folder:
            try:
                active = str(server.photos_dir.resolve())
                configured = str(Path(configured_folder).expanduser().resolve())
            except OSError:
                reasons.append("folder")
            else:
                if active != configured:
                    reasons.append("folder")
        if server.port != configured_port:
            reasons.append("port")
        if not reasons:
            return ""
        joined = " and ".join(reasons)
        return (
            "<span style='color:#a60;'>Configured "
            f"{joined} differ(s) from the active listener — restart listen to apply.</span>"
        )

    @classmethod
    def _phone_status_html(cls, device_id: str, last_at: float | None, last_event: str) -> str:
        if not device_id or last_at is None:
            return (
                "<b>Phone:</b> not connected this session<br>"
                "<span style='color:#666;'>Status updates when Android completes a "
                "handshake while the PC is listening.</span>"
            )

        age = max(0.0, time.time() - last_at)
        when = datetime.fromtimestamp(last_at, tz=UTC).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        if len(device_id) <= cls._DEVICE_ID_SHORT_LEN:
            short_id = device_id
        else:
            short_id = f"{device_id[: cls._DEVICE_ID_PREFIX_LEN]}…"
        if age <= cls._PHONE_ACTIVE_SECONDS:
            state = f"<span style='color:#080;'>active</span> ({last_event or 'activity'})"
        else:
            state = f"last seen {cls._format_age(age)} ago ({last_event or 'activity'})"

        return f"<b>Phone:</b> {state}<br><b>Device id:</b> <code>{short_id}</code><br><b>Last activity:</b> {when}"

    @classmethod
    def _status_html(cls, configured_folder: str, configured_port: int) -> str:
        server = get_shared_server()
        listening = server is not None and server.is_running
        ips = list_lan_ipv4()
        ip_text = ", ".join(ips) if ips else "not detected"

        if listening and server is not None:
            listen_line = (
                f"<b>Listener:</b> running on port {server.port}<br>"
                f"<b>Active folder:</b> {server.photos_dir}<br>"
                f"<b>Token:</b> <code>{server.token}</code><br>"
                f"<b>Session uploads:</b> {server.stats.uploads_ok} "
                f"({server.stats.uploads_bytes} bytes)<br>"
                f"<b>Last server message:</b> {server.stats.last_message or '—'}"
            )
            mismatch_note = cls._listener_mismatch_note(
                server,
                configured_folder=configured_folder,
                configured_port=configured_port,
            )
            if mismatch_note:
                listen_line += f"<br>{mismatch_note}"
        else:
            listen_line = (
                f"<b>Listener:</b> stopped<br>"
                f"<b>Configured folder:</b> {configured_folder or '(not set)'}<br>"
                f"<b>Configured port:</b> {configured_port}"
            )

        phone = get_phone_connection_info()
        phone_line = cls._phone_status_html(phone.device_id, phone.last_at, phone.last_event)

        return f"{listen_line}<br><br><b>LAN IP:</b> {ip_text}<br><br>{phone_line}"
