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

Photo Sync settings, LAN listener, QR pairing, and phone connection status.

Configures `path_photos` / `photo_sync_port`, starts the receiver, and shows the
QR + confirmation number for the Android app.

<details>
<summary>Code:</summary>

```python
class OnPhotoSync(ActionBase):

    icon = "📡"
    title = "Photo sync"
    description = "LAN Photo Sync: folder, listen, QR pairing, phone status"
    cli_available = False
    _dialog: ClassVar[QDialog | None] = None

    CONFIG_FOLDER_KEY = "path_photos"
    CONFIG_PORT_KEY = "photo_sync_port"
    _MAX_TCP_PORT = 65535
    _PHONE_ACTIVE_SECONDS = 45
    _SECONDS_PER_MINUTE = 60
    _DEVICE_ID_SHORT_LEN = 16
    _DEVICE_ID_PREFIX_LEN = 12

    @ActionBase.handle_exceptions("photo sync")
    def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        """Open the combined Photo Sync dialog."""
        if OnPhotoSync._dialog is not None:
            OnPhotoSync._dialog.raise_()
            OnPhotoSync._dialog.activateWindow()
            return

        dialog = self._build_dialog()
        OnPhotoSync._dialog = dialog
        dialog.show()

    def _build_dialog(self) -> QDialog:
        dialog = QDialog()
        dialog.setWindowTitle("Photo sync")
        dialog.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)  # noqa: FBT003
        dialog.resize(560, 780)
        layout = QVBoxLayout(dialog)

        title = QLabel("Photo Sync")
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        hint = QLabel(
            "Save the photos folder, start listening, then scan the QR on the phone "
            "and choose the confirmation number shown here."
        )
        hint.setWordWrap(True)
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
        port_spin.setValue(self._configured_port())
        form.addRow("Listen port:", port_spin)
        layout.addLayout(form)

        listen_row = QHBoxLayout()
        start_btn = QPushButton("Start listening")
        stop_btn = QPushButton("Stop listening")
        save_btn = QPushButton("Save settings")
        listen_row.addWidget(start_btn)
        listen_row.addWidget(stop_btn)
        listen_row.addWidget(save_btn)
        layout.addLayout(listen_row)

        code_label = QLabel("—")
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        code_label.setStyleSheet("font-size: 56px; font-weight: 700; letter-spacing: 4px;")
        layout.addWidget(code_label)

        ip_row = QHBoxLayout()
        ip_combo = QComboBox()
        ip_combo.setMinimumWidth(180)
        ip_row.addWidget(QLabel("QR host IP:"))
        ip_row.addWidget(ip_combo, stretch=1)
        layout.addLayout(ip_row)

        ip_warning = QLabel()
        ip_warning.setWordWrap(True)
        ip_warning.setStyleSheet("color: #a60;")
        layout.addWidget(ip_warning)

        qr_label = QLabel()
        qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_label.setMinimumHeight(220)
        layout.addWidget(qr_label)

        status = QLabel()
        status.setWordWrap(True)
        status.setTextFormat(Qt.TextFormat.RichText)
        status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(status)

        log = QTextEdit()
        log.setReadOnly(True)
        log.setMinimumHeight(100)
        layout.addWidget(log, stretch=1)

        close_btn = QPushButton("Close")
        layout.addWidget(close_btn)

        def browse() -> None:
            chosen = self.dialogs.get_existing_directory(
                "Select photos sync folder",
                folder_edit.text().strip() or str(Path.home()),
            )
            if chosen is not None:
                folder_edit.setText(str(chosen))

        def save_settings(*, quiet: bool = False) -> Path | None:
            folder = folder_edit.text().strip().strip("\"'")
            if not folder:
                QMessageBox.warning(dialog, "Photo sync", "Photos folder cannot be empty.")
                return None
            path = Path(folder).expanduser()
            if not path.exists():
                try:
                    path.mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    QMessageBox.warning(dialog, "Photo sync", f"Cannot create folder:\n{exc}")
                    return None
            if not path.is_dir():
                QMessageBox.warning(dialog, "Photo sync", "Selected path is not a folder.")
                return None
            resolved = str(path.resolve())
            port = int(port_spin.value())
            self._save_config_value(self.CONFIG_FOLDER_KEY, resolved)
            self._save_config_value(self.CONFIG_PORT_KEY, port)
            self.invalidate_config_cache()
            folder_edit.setText(resolved)
            if not quiet:
                self.add_line(f"Photo sync folder: {resolved}")
                self.add_line(f"Photo sync port: {port}")
                self.show_toast("Photo sync settings saved")
            return Path(resolved)

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
                png = make_qr_png_bytes(uri)
                pixmap = QPixmap()
                pixmap.loadFromData(png)
                qr_label.setPixmap(pixmap)
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
                ip_warning.clear()

        def refresh_status() -> None:
            server = get_shared_server()
            listening = server is not None and server.is_running
            if listening != stop_btn.isEnabled():
                refresh_ip_combo(keep_selection=True)
            status.setText(
                self._status_html(
                    folder_edit.text().strip(),
                    int(port_spin.value()),
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
            else:
                if not listening:
                    log.clear()
                dialog.setWindowTitle("Photo sync")

        def start_listen() -> None:
            photos_dir = save_settings(quiet=True)
            if photos_dir is None:
                return
            existing = get_shared_server()
            if existing is not None and existing.is_running:
                refresh_ip_combo()
                refresh_status()
                return
            port = int(port_spin.value())
            server = PhotoSyncServer(photos_dir, port=port)
            try:
                server.start()
            except OSError as exc:
                QMessageBox.warning(
                    dialog,
                    "Photo sync",
                    f"Cannot listen on port {port}:\n{exc}\n\n"
                    "Check Windows Firewall or choose another port.",
                )
                return
            set_shared_server(server)
            self.add_line(f"Photo sync listening on port {port}")
            self.add_line(f"Confirm code: {server.confirm_code}")
            self.show_toast("Photo sync listening")
            refresh_ip_combo(keep_selection=False)
            refresh_status()

        def stop_listen() -> None:
            server = get_shared_server()
            if server is not None and server.is_running:
                server.stop()
            set_shared_server(None)
            self.add_line("Photo sync listener stopped.")
            self.show_toast("Photo sync stopped")
            update_pairing_ui()
            refresh_status()

        browse_btn.clicked.connect(browse)
        save_btn.clicked.connect(lambda: save_settings(quiet=False))
        start_btn.clicked.connect(start_listen)
        stop_btn.clicked.connect(stop_listen)
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
            if OnPhotoSync._dialog is dialog:
                OnPhotoSync._dialog = None

        dialog.finished.connect(on_finished)
        return dialog

    def _configured_port(self) -> int:
        port_raw = self.config.get(self.CONFIG_PORT_KEY, DEFAULT_PORT)
        try:
            port_value = int(port_raw)
        except (TypeError, ValueError):
            return DEFAULT_PORT
        if not (1 <= port_value <= self._MAX_TCP_PORT):
            return DEFAULT_PORT
        return port_value

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
    def _status_html(cls, configured_folder: str, configured_port: int, *, qr_host: str) -> str:
        server = get_shared_server()
        listening = server is not None and server.is_running
        ips = list_lan_ipv4()
        ip_text = ", ".join(ips) if ips else "not detected"
        if listening and server is not None:
            listen_line = (
                f"<b>Listener:</b> running on port {server.port}<br>"
                f"<b>Active folder:</b> {server.photos_dir}<br>"
                f"<b>QR host:</b> {qr_host or '—'}<br>"
                f"<b>Session uploads:</b> {server.stats.uploads_ok} "
                f"({server.stats.uploads_bytes} bytes)<br>"
                f"<b>Last server message:</b> {server.stats.last_message or '—'}"
            )
        else:
            listen_line = (
                f"<b>Listener:</b> stopped<br>"
                f"<b>Configured folder:</b> {configured_folder or '(not set)'}<br>"
                f"<b>Configured port:</b> {configured_port}"
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

Open the combined Photo Sync dialog.

<details>
<summary>Code:</summary>

```python
def execute(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        if OnPhotoSync._dialog is not None:
            OnPhotoSync._dialog.raise_()
            OnPhotoSync._dialog.activateWindow()
            return

        dialog = self._build_dialog()
        OnPhotoSync._dialog = dialog
        dialog.show()
```

</details>
