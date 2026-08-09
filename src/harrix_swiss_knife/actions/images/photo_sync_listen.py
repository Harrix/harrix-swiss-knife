"""Start/stop LAN photo sync listener for phone → PC transfers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from harrix_swiss_knife.actions.common.base import ActionBase
from harrix_swiss_knife.photo_sync.lan import list_lan_ipv4, pairing_uri
from harrix_swiss_knife.photo_sync.qr_image import make_qr_png_bytes
from harrix_swiss_knife.photo_sync.server import (
    DEFAULT_PORT,
    PhotoSyncServer,
    get_shared_server,
    set_shared_server,
)

_MAX_TCP_PORT = 65535


class OnPhotoSyncListen(ActionBase):
    """Listen on LAN for one-way Camera photo sync from the Android app.

    Starts a local HTTP receiver that writes into `path_photos`. Shows a QR code
    (host, port, token, confirm code) and a large confirmation number for the
    phone to select. Run again while listening to stop the server.

    """

    icon = "📡"
    title = "Photo sync listen (LAN)"
    description = "Receive Camera photos from Android over Wi-Fi"
    cli_available = False
    _dialog: ClassVar[QDialog | None] = None

    @ActionBase.handle_exceptions("photo sync listen")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Toggle the LAN photo sync listener and show pairing UI."""
        existing = get_shared_server()
        if existing is not None and existing.is_running:
            existing.stop()
            set_shared_server(None)
            if OnPhotoSyncListen._dialog is not None:
                OnPhotoSyncListen._dialog.close()
                OnPhotoSyncListen._dialog = None
            self.add_line("Photo sync listener stopped.")
            self.show_toast("Photo sync stopped")
            return

        path_photos = (self.config.get("path_photos") or "").strip()
        if not path_photos:
            self.add_line("❌ path_photos is not set in config.json.")
            self.show_result()
            return
        photos_dir = Path(path_photos)
        if not photos_dir.exists():
            try:
                photos_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                self.add_line(f"❌ Cannot create path_photos ({photos_dir}): {exc}")
                self.show_result()
                return

        port_raw = self.config.get("photo_sync_port", DEFAULT_PORT)
        try:
            port = int(port_raw)
        except (TypeError, ValueError):
            port = DEFAULT_PORT
        if not (1 <= port <= _MAX_TCP_PORT):
            port = DEFAULT_PORT

        server = PhotoSyncServer(photos_dir, port=port)
        try:
            server.start()
        except OSError as exc:
            self.add_line(
                f"❌ Cannot listen on port {port}: {exc}. "
                "Check Windows Firewall or choose another photo_sync_port in config.json."
            )
            self.show_result()
            return

        set_shared_server(server)
        ips = list_lan_ipv4()
        host = ips[0] if ips else "127.0.0.1"
        uri = pairing_uri(
            host=host,
            port=port,
            token=server.token,
            confirm_code=server.confirm_code,
        )
        self.add_line(f"Photo sync listening on port {port}")
        self.add_line(f"LAN IP: {', '.join(ips) if ips else '(none detected)'}")
        self.add_line(f"Confirm code: {server.confirm_code}")
        self.add_line(f"Saving to: {photos_dir}")
        self.show_toast("Photo sync listening")

        dialog = self._build_dialog(server, ips=ips, uri=uri)
        OnPhotoSyncListen._dialog = dialog
        dialog.show()

    def _build_dialog(
        self,
        server: PhotoSyncServer,
        *,
        ips: list[str],
        uri: str,
    ) -> QDialog:
        dialog = QDialog()
        dialog.setWindowTitle("Photo sync — listening")
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)  # noqa: FBT003
        dialog.resize(520, 700)
        layout = QVBoxLayout(dialog)

        title = QLabel("Scan this QR on the phone")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        hint = QLabel("Then on the phone choose the same confirmation number shown below.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        code_label = QLabel(server.confirm_code)
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setStyleSheet("font-size: 56px; font-weight: 700; letter-spacing: 4px;")
        layout.addWidget(code_label)

        info = QLabel(
            f"<b>Folder:</b> {server.photos_dir}<br>"
            f"<b>LAN IP:</b> {', '.join(ips) if ips else 'not detected'}<br>"
            f"<b>Port:</b> {server.port}"
        )
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setWordWrap(True)
        info.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(info)

        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        png = make_qr_png_bytes(uri)
        pixmap = QPixmap()
        pixmap.loadFromData(png)
        qr_label.setPixmap(pixmap)
        layout.addWidget(qr_label)

        log = QTextEdit()
        log.setReadOnly(True)
        log.setMinimumHeight(120)
        layout.addWidget(log)

        buttons = QHBoxLayout()
        stop_btn = QPushButton("Stop listening")
        close_btn = QPushButton("Hide")
        buttons.addWidget(stop_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)

        def refresh_log() -> None:
            log.setPlainText("\n".join(server.stats.log_lines))
            stats = (
                f"Uploads: {server.stats.uploads_ok}  |  "
                f"Bytes: {server.stats.uploads_bytes}  |  "
                f"{server.stats.last_message}"
            )
            dialog.setWindowTitle(f"Photo sync — {stats}")

        timer = QTimer(dialog)
        timer.setInterval(500)
        timer.timeout.connect(refresh_log)
        timer.start()
        refresh_log()
        server.set_on_change(lambda: None)  # timer polls stats

        def stop() -> None:
            if server.is_running:
                server.stop()
            set_shared_server(None)
            timer.stop()
            dialog.close()
            OnPhotoSyncListen._dialog = None
            self.add_line("Photo sync listener stopped.")

        def hide() -> None:
            dialog.hide()

        stop_btn.clicked.connect(stop)
        close_btn.clicked.connect(hide)

        def on_finished() -> None:
            # Closing the dialog does not stop the server; only Stop / toggle does.
            if OnPhotoSyncListen._dialog is dialog:
                OnPhotoSyncListen._dialog = None

        dialog.finished.connect(on_finished)
        return dialog
