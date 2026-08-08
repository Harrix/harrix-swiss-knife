---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `photo_sync_listen.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnPhotoSyncListen`](#%EF%B8%8F-class-onphotosynclisten)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnPhotoSyncListen`

```python
class OnPhotoSyncListen(ActionBase)
```

Listen on LAN for one-way Camera photo sync from the Android app.

Starts a local HTTP receiver that writes into `path_photos`. Shows IP, PIN
(token), and a QR pairing URI. Run again while listening to stop the server.

<details>
<summary>Code:</summary>

```python
class OnPhotoSyncListen(ActionBase):

    icon = "📡"
    title = "Photo sync listen (LAN)"
    description = "Receive Camera photos from Android over Wi‑Fi"
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
        if not (1 <= port <= 65535):
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
        uri = pairing_uri(host=host, port=port, token=server.token)
        self.add_line(f"Photo sync listening on port {port}")
        self.add_line(f"LAN IP: {', '.join(ips) if ips else '(none detected)'}")
        self.add_line(f"Token: {server.token}")
        self.add_line(f"Pairing URI: {uri}")
        self.add_line(f"Saving to: {photos_dir}")
        self.show_toast("Photo sync listening")

        dialog = self._build_dialog(server, ips=ips, host=host, uri=uri)
        OnPhotoSyncListen._dialog = dialog
        dialog.show()

    def _build_dialog(
        self,
        server: PhotoSyncServer,
        *,
        ips: list[str],
        host: str,
        uri: str,
    ) -> QDialog:
        dialog = QDialog()
        dialog.setWindowTitle("Photo sync — listening")
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        dialog.resize(520, 640)
        layout = QVBoxLayout(dialog)

        title = QLabel("Waiting for Android Photo Sync")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        info = QLabel(
            f"<b>Folder:</b> {server.photos_dir}<br>"
            f"<b>Port:</b> {server.port}<br>"
            f"<b>LAN IP:</b> {', '.join(ips) if ips else 'not detected'}<br>"
            f"<b>Token:</b> <code>{server.token}</code><br>"
            f"<b>Primary host:</b> {host}"
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

        uri_label = QLabel(uri)
        uri_label.setWordWrap(True)
        uri_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(uri_label)

        log = QTextEdit()
        log.setReadOnly(True)
        log.setMinimumHeight(140)
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
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Toggle the LAN photo sync listener and show pairing UI.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
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
        if not (1 <= port <= 65535):
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
        uri = pairing_uri(host=host, port=port, token=server.token)
        self.add_line(f"Photo sync listening on port {port}")
        self.add_line(f"LAN IP: {', '.join(ips) if ips else '(none detected)'}")
        self.add_line(f"Token: {server.token}")
        self.add_line(f"Pairing URI: {uri}")
        self.add_line(f"Saving to: {photos_dir}")
        self.show_toast("Photo sync listening")

        dialog = self._build_dialog(server, ips=ips, host=host, uri=uri)
        OnPhotoSyncListen._dialog = dialog
        dialog.show()
```

</details>
