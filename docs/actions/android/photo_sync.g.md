---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `photo_sync.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `OnPhotoSync`](#%EF%B8%8F-class-onphotosync)
  - [⚙️ Method `execute`](#%EF%B8%8F-method-execute)

</details>

## 🏛️ Class `OnPhotoSync`

```python
class OnPhotoSync(ActionBase)
```

Photo Sync listen UI with QR pairing; folder path lives on a Settings tab.

Uses a fixed listen port (`DEFAULT_PORT`). The port is embedded in the QR, so
neither desktop nor phone needs a port field.

<details>
<summary>Code:</summary>

```python
class OnPhotoSync(ActionBase):

    icon = "📡"
    title = "Photo sync"
    description = "LAN Photo Sync: listen, QR pairing, phone status"
    cli_available = False
    _dialog: ClassVar[QDialog | None] = None

    CONFIG_FOLDER_KEY = "path_photos"
    _PHONE_ACTIVE_SECONDS = 45
    _SECONDS_PER_MINUTE = 60
    _DEVICE_ID_SHORT_LEN = 16
    _DEVICE_ID_PREFIX_LEN = 12
    _QR_BOX_SIZE = 12
    _QR_MIN_PX = 360

    @ActionBase.handle_exceptions("photo sync")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the Photo Sync dialog."""
        if OnPhotoSync._dialog is not None:
            OnPhotoSync._dialog.raise_()
            OnPhotoSync._dialog.activateWindow()
            return

        # Paint toast before any dialog work so the user sees feedback immediately.
        self.show_toast("Starting Photo sync… Indexing may take a while.", duration=12000)
        app = QApplication.instance()
        if app is not None:
            app.processEvents()
        dialog, start_listen = self._build_dialog()
        OnPhotoSync._dialog = dialog
        dialog.show()
        if app is not None:
            app.processEvents()
        # Defer listen start so toast + window paint before server setup.
        QTimer.singleShot(50, start_listen)

    def _build_dialog(self) -> tuple[QDialog, Any]:  # Any: nested start_listen callback
        dialog = QDialog()
        dialog.setWindowTitle("Photo sync")
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)  # noqa: FBT003
        dialog.resize(980, 900)
        root = QVBoxLayout(dialog)

        tabs = QTabWidget()
        root.addWidget(tabs, stretch=1)

        listen_page = QWidget()
        listen_layout = QVBoxLayout(listen_page)

        title = QLabel("Photo Sync")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        listen_layout.addWidget(title)

        hint = QLabel(
            "Start listening, scan the QR on the phone, then choose the confirmation "
            "number shown below. Both devices must be on the same Wi-Fi (VPN off)."
        )
        hint.setWordWrap(True)
        listen_layout.addWidget(hint)

        listen_row = QHBoxLayout()
        start_btn = QPushButton("Start listening")
        stop_btn = QPushButton("Stop listening")
        listen_row.addWidget(start_btn)
        listen_row.addWidget(stop_btn)
        listen_layout.addLayout(listen_row)

        columns = QHBoxLayout()
        left = QVBoxLayout()
        right = QVBoxLayout()

        code_label = QLabel("—")
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setStyleSheet("font-size: 56px; font-weight: 700; letter-spacing: 4px;")
        left.addWidget(code_label)

        ip_row = QHBoxLayout()
        ip_combo = QComboBox()
        ip_combo.setMinimumWidth(180)
        ip_row.addWidget(QLabel("QR host IP:"))
        ip_row.addWidget(ip_combo, stretch=1)
        left.addLayout(ip_row)

        ip_warning = QLabel()
        ip_warning.setWordWrap(True)
        ip_warning.setStyleSheet("color: #a60;")
        left.addWidget(ip_warning)

        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_label.setMinimumSize(self._QR_MIN_PX, self._QR_MIN_PX)
        qr_label.setStyleSheet("background: white; border: 1px solid #ccc;")
        left.addWidget(qr_label, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter)
        left.addStretch(1)

        status = QLabel()
        status.setWordWrap(True)
        status.setTextFormat(Qt.TextFormat.RichText)
        status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        right.addWidget(status)

        log = QTextEdit()
        log.setReadOnly(True)
        log.setMinimumWidth(320)
        right.addWidget(log, stretch=1)

        columns.addLayout(left, stretch=0)
        columns.addLayout(right, stretch=1)
        listen_layout.addLayout(columns, stretch=1)

        listen_scroll = QScrollArea()
        listen_scroll.setWidgetResizable(True)
        listen_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        listen_scroll.setWidget(listen_page)
        tabs.addTab(listen_scroll, "Listen")

        settings_page = QWidget()
        settings_layout = QVBoxLayout(settings_page)
        settings_hint = QLabel(
            "Photos folder for incoming Camera sync. New files go into the folder root; "
            f"existing files are matched by hash in all subfolders. Listen port is fixed "
            f"({DEFAULT_PORT}) and sent inside the QR code."
        )
        settings_hint.setWordWrap(True)
        settings_layout.addWidget(settings_hint)

        form = QFormLayout()
        folder_edit = QLineEdit(self._configured_folder_display())
        folder_row = QHBoxLayout()
        folder_row.addWidget(folder_edit, stretch=1)
        browse_btn = QPushButton("Browse…")
        folder_row.addWidget(browse_btn)
        form.addRow("Photos folder:", folder_row)
        settings_layout.addLayout(form)

        save_btn = QPushButton("Save folder")
        settings_layout.addWidget(save_btn)
        settings_layout.addStretch(1)
        tabs.addTab(settings_page, "Settings")

        close_btn = QPushButton("Close")
        root.addWidget(close_btn)

        def browse() -> None:
            chosen = self.dialogs.get_existing_directory(
                "Select photos sync folder",
                folder_edit.text().strip() or str(Path.home()),
            )
            if chosen is not None:
                folder_edit.setText(self._path_for_config(chosen))

        def save_folder(*, quiet: bool = False) -> Path | None:
            folder = folder_edit.text().strip().strip("\"'")
            if not folder:
                QMessageBox.warning(dialog, "Photo sync", "Photos folder cannot be empty.")
                tabs.setCurrentIndex(1)
                return None
            path = Path(folder).expanduser()
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    QMessageBox.warning(dialog, "Photo sync", f"Cannot create folder:\n{exc}")
                    tabs.setCurrentIndex(1)
                    return None
            if not path.is_dir():
                QMessageBox.warning(dialog, "Photo sync", "Selected path is not a folder.")
                tabs.setCurrentIndex(1)
                return None
            stored = self._path_for_config(path.resolve())
            self._save_config_value(self.CONFIG_FOLDER_KEY, stored)
            self.invalidate_config_cache()
            folder_edit.setText(stored)
            if not quiet:
                self.add_line(f"Photo sync folder: {stored}")
                self.show_toast("Photo sync folder saved")
            return Path(stored)

        def refresh_ip_combo(*, keep_selection: bool = True) -> None:
            current = ip_combo.currentText().strip()
            ips = list_lan_ipv4()
            ip_combo.blockSignals(True)
            ip_combo.clear()
            if ips:
                ip_combo.addItems(ips)
                if keep_selection and current in ips:
                    ip_combo.setCurrentText(current)
            else:
                ip_combo.addItem("127.0.0.1")
            ip_combo.blockSignals(False)
            update_pairing_ui()

        def update_pairing_ui() -> None:
            server = get_shared_server()
            listening = server is not None and server.is_running
            start_btn.setEnabled(not listening)
            stop_btn.setEnabled(listening)
            ip_combo.setEnabled(listening)
            host = ip_combo.currentText().strip() or "127.0.0.1"
            if listening and server is not None:
                code_label.setText(server.confirm_code)
                uri = pairing_uri(
                    host=host,
                    port=server.port,
                    token=server.token,
                    confirm_code=server.confirm_code,
                )
                png = make_qr_png_bytes(uri, box_size=self._QR_BOX_SIZE)
                pixmap = QPixmap()
                pixmap.loadFromData(png)
                if (
                    pixmap.width() < self._QR_MIN_PX
                    or pixmap.height() < self._QR_MIN_PX
                ):
                    pixmap = pixmap.scaled(
                        self._QR_MIN_PX,
                        self._QR_MIN_PX,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                qr_label.setPixmap(pixmap)
                qr_label.setFixedSize(pixmap.size())
                if is_likely_virtual_lan_ip(host):
                    ip_warning.setText(
                        "This IP looks like a VirtualBox/VM adapter. "
                        "The phone on Wi-Fi usually cannot reach it — "
                        "pick your real Wi-Fi IP (often 192.168.0.x / 192.168.1.x)."
                    )
                else:
                    ip_warning.clear()
            else:
                code_label.setText("—")
                qr_label.clear()
                qr_label.setFixedSize(self._QR_MIN_PX, self._QR_MIN_PX)
                ip_warning.clear()

        library_ready_toast_shown = False

        def refresh_status() -> None:
            nonlocal library_ready_toast_shown
            server = get_shared_server()
            listening = server is not None and server.is_running
            if listening != stop_btn.isEnabled():
                refresh_ip_combo(keep_selection=True)
            status.setText(
                self._status_html(
                    folder_edit.text().strip(),
                    qr_host=ip_combo.currentText().strip(),
                )
            )
            if listening and server is not None:
                log.setPlainText("\n".join(server.stats.log_lines))
                dialog.setWindowTitle(
                    "Photo sync — "
                    f"Uploads: {server.stats.uploads_ok} | "
                    f"{server.stats.last_message}"
                )
                if (
                    not library_ready_toast_shown
                    and server.stats.last_message.startswith("Photo library ready")
                ):
                    library_ready_toast_shown = True
                    self.show_toast(server.stats.last_message, duration=4000)
            else:
                if not listening:
                    log.clear()
                dialog.setWindowTitle("Photo sync")

        def start_listen() -> None:
            nonlocal library_ready_toast_shown
            photos_dir = save_folder(quiet=True)
            if photos_dir is None:
                return
            existing = get_shared_server()
            if existing is not None and existing.is_running:
                refresh_ip_combo()
                refresh_status()
                return
            self.show_toast("Indexing photo library… This can take a while.", duration=12000)
            self.add_line("Starting listener; photo library indexes in background…")
            app = QApplication.instance()
            if app is not None:
                app.processEvents()
            server = PhotoSyncServer(photos_dir, port=DEFAULT_PORT)
            try:
                server.start()
            except OSError as exc:
                QMessageBox.warning(
                    dialog,
                    "Photo sync",
                    f"Cannot listen on port {DEFAULT_PORT}:\n{exc}\n\n"
                    "Check Windows Firewall or free the port.",
                )
                return
            set_shared_server(server)
            library_ready_toast_shown = False
            self.add_line(f"Photo sync listening on port {DEFAULT_PORT}")
            self.add_line(f"Confirm code: {server.confirm_code}")
            self.show_toast("Photo sync listening. Indexing continues in background…", duration=5000)
            refresh_ip_combo(keep_selection=False)
            refresh_status()

        def stop_listen(*, quiet: bool = False) -> None:
            server = get_shared_server()
            was_running = False
            if server is not None and server.is_running:
                server.stop()
                was_running = True
            set_shared_server(None)
            if quiet:
                return
            if was_running:
                self.add_line("Photo sync listener stopped.")
                self.show_toast("Photo sync stopped")
            update_pairing_ui()
            refresh_status()

        browse_btn.clicked.connect(browse)
        save_btn.clicked.connect(lambda: save_folder(quiet=False))
        start_btn.clicked.connect(start_listen)
        stop_btn.clicked.connect(lambda: stop_listen(quiet=False))
        close_btn.clicked.connect(dialog.close)
        ip_combo.currentTextChanged.connect(lambda _text: update_pairing_ui())

        timer = QTimer(dialog)
        timer.setInterval(1000)
        timer.timeout.connect(refresh_status)
        timer.start()

        refresh_ip_combo(keep_selection=False)
        update_pairing_ui()
        refresh_status()

        def on_finished() -> None:
            timer.stop()
            # Closing the window ends the session: phone can no longer sync.
            stop_listen(quiet=True)
            if OnPhotoSync._dialog is dialog:
                OnPhotoSync._dialog = None

        dialog.finished.connect(on_finished)
        return dialog, start_listen

    def _configured_folder_display(self) -> str:
        raw = (self.config.get(self.CONFIG_FOLDER_KEY) or "").strip()
        if not raw:
            return ""
        return self._path_for_config(Path(raw))

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
    def _path_for_config(path: Path | str) -> str:
        """Store Windows paths with forward slashes in `config.json`."""
        return Path(path).expanduser().resolve().as_posix()

    @classmethod
    def _phone_status_html(cls, device_id: str, last_at: float | None, last_event: str) -> str:
        if not device_id or last_at is None:
            return (
                "<b>Phone:</b> not connected this session<br>"
                "<span style='color:#666;'>Updates after a successful handshake.</span>"
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
        return (
            f"<b>Phone:</b> {state}<br>"
            f"<b>Device id:</b> <code>{short_id}</code><br>"
            f"<b>Last activity:</b> {when}"
        )

    @classmethod
    def _status_html(cls, configured_folder: str, *, qr_host: str) -> str:
        server = get_shared_server()
        listening = server is not None and server.is_running
        ips = list_lan_ipv4()
        ip_text = ", ".join(ips) if ips else "not detected"
        if listening and server is not None:
            listen_line = (
                f"<b>Listener:</b> running (port {server.port})<br>"
                f"<b>Folder:</b> {server.photos_dir.as_posix()}<br>"
                f"<b>QR host:</b> {qr_host or '—'}<br>"
                f"<b>Uploads:</b> {server.stats.uploads_ok} "
                f"({server.stats.uploads_bytes} bytes) — "
                f"{server.stats.last_message or '—'}"
            )
        else:
            listen_line = (
                f"<b>Listener:</b> stopped<br>"
                f"<b>Folder:</b> {configured_folder or '(set in Settings tab)'}"
            )
        phone = get_phone_connection_info()
        phone_line = cls._phone_status_html(phone.device_id, phone.last_at, phone.last_event)
        return f"{listen_line}<br><br><b>LAN IPs:</b> {ip_text}<br><br>{phone_line}"
```

</details>

### ⚙️ Method `execute`

```python
def execute(self, *args: Any, **kwargs: Any) -> None
```

Open the Photo Sync dialog.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if OnPhotoSync._dialog is not None:
            OnPhotoSync._dialog.raise_()
            OnPhotoSync._dialog.activateWindow()
            return

        # Paint toast before any dialog work so the user sees feedback immediately.
        self.show_toast("Starting Photo sync… Indexing may take a while.", duration=12000)
        app = QApplication.instance()
        if app is not None:
            app.processEvents()
        dialog, start_listen = self._build_dialog()
        OnPhotoSync._dialog = dialog
        dialog.show()
        if app is not None:
            app.processEvents()
        # Defer listen start so toast + window paint before server setup.
        QTimer.singleShot(50, start_listen)
```

</details>
