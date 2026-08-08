---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `server.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `PhotoSyncServer`](#%EF%B8%8F-class-photosyncserver)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `index_for`](#%EF%B8%8F-method-index_for)
  - [⚙️ Method `is_running (property)`](#%EF%B8%8F-method-is_running-property)
  - [⚙️ Method `set_on_change`](#%EF%B8%8F-method-set_on_change)
  - [⚙️ Method `start`](#%EF%B8%8F-method-start)
  - [⚙️ Method `stop`](#%EF%B8%8F-method-stop)
- [🏛️ Class `SyncStats`](#%EF%B8%8F-class-syncstats)
  - [⚙️ Method `note`](#%EF%B8%8F-method-note)
- [🔧 Function `get_shared_server`](#-function-get_shared_server)
- [🔧 Function `set_shared_server`](#-function-set_shared_server)

</details>

## 🏛️ Class `PhotoSyncServer`

```python
class PhotoSyncServer
```

Tokenized LAN HTTP server that receives photos into `photos_dir`.

<details>
<summary>Code:</summary>

```python
class PhotoSyncServer:

    def __init__(self, photos_dir: Path, port: int = DEFAULT_PORT) -> None:
        self.photos_dir = photos_dir
        self.port = port
        self.token = secrets.token_urlsafe(18)
        self.stats = SyncStats()
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._indexes: dict[str, DeviceSyncIndex] = {}
        self._index_lock = threading.Lock()
        self._on_change: Callable[[], None] | None = None

    def index_for(self, device_id: str) -> DeviceSyncIndex:
        """Return (and cache) the sync index for a device."""
        with self._index_lock:
            existing = self._indexes.get(device_id)
            if existing is not None:
                return existing
            created = DeviceSyncIndex(self.photos_dir, device_id)
            self._indexes[device_id] = created
            return created

    @property
    def is_running(self) -> bool:
        """Whether the listener thread is active."""
        return self._thread is not None and self._thread.is_alive()

    def set_on_change(self, callback: Callable[[], None] | None) -> None:
        """Register a UI refresh callback invoked after status updates."""
        self._on_change = callback

    def start(self) -> None:
        """Bind and start serving in a daemon thread."""
        if self.is_running:
            return
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        handler = self._make_handler()
        try:
            self._httpd = ThreadingHTTPServer(("0.0.0.0", self.port), handler)
        except OSError:
            self.stats.note(f"Failed to bind port {self.port} (firewall or in use)")
            raise
        self._thread = threading.Thread(target=self._httpd.serve_forever, name="photo-sync-http", daemon=True)
        self._thread.start()
        self.stats.note(f"Listening on port {self.port}")
        self._notify()

    def stop(self) -> None:
        """Stop the HTTP server."""
        httpd = self._httpd
        self._httpd = None
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()
        thread = self._thread
        self._thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self.stats.note("Stopped")
        self._notify()

    def _make_handler(self) -> type[BaseHTTPRequestHandler]:
        server = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                logger.debug("photo-sync: " + format, *args)

            def do_GET(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path == "/v1/health":
                    self._json_response(200, {"ok": True, "protocolVersion": PROTOCOL_VERSION})
                    return
                self._json_response(404, {"error": "not_found"})

            def do_POST(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                body = self._read_json_body()
                if body is None:
                    self._json_response(400, {"error": "invalid_json"})
                    return
                if parsed.path == "/v1/handshake":
                    self._handle_handshake(body)
                    return
                if parsed.path == "/v1/manifest":
                    self._handle_manifest(body)
                    return
                self._json_response(404, {"error": "not_found"})

            def do_PUT(self) -> None:  # noqa: N802
                parsed = urlparse(self.path)
                if parsed.path != "/v1/upload":
                    self._json_response(404, {"error": "not_found"})
                    return
                self._handle_upload(parsed)

            def _handle_handshake(self, body: dict[str, Any]) -> None:
                if not self._authorized(body.get("token")):
                    self._json_response(401, {"error": "unauthorized"})
                    return
                device_id = str(body.get("deviceId", "")).strip()
                if not device_id:
                    self._json_response(400, {"error": "device_id_required"})
                    return
                server.stats.note(f"Handshake from {device_id[:12]}…")
                server._notify()
                self._json_response(200, {"ok": True, "protocolVersion": PROTOCOL_VERSION})

            def _handle_manifest(self, body: dict[str, Any]) -> None:
                if not self._authorized(body.get("token")):
                    self._json_response(401, {"error": "unauthorized"})
                    return
                device_id = str(body.get("deviceId", "")).strip()
                items = body.get("items")
                if not device_id or not isinstance(items, list):
                    self._json_response(400, {"error": "invalid_manifest"})
                    return
                index = server.index_for(device_id)
                needed = index.needed_media_ids(items)
                server.stats.note(f"Manifest: {len(items)} items, {len(needed)} needed")
                server._notify()
                self._json_response(200, {"needed": needed})

            def _handle_upload(self, parsed: Any) -> None:
                query = parse_qs(parsed.query)
                token = (query.get("token") or [""])[0]
                if not self._authorized(token):
                    self._json_response(401, {"error": "unauthorized"})
                    return
                device_id = (query.get("deviceId") or [""])[0].strip()
                media_id = (query.get("mediaId") or [""])[0].strip()
                content_hash = (query.get("contentHash") or [""])[0].strip().lower()
                display_name = (query.get("displayName") or [""])[0]
                mime_type = (query.get("mimeType") or [""])[0]
                try:
                    date_taken = int((query.get("dateTaken") or ["0"])[0])
                except ValueError:
                    date_taken = 0
                if not device_id or not media_id or not content_hash:
                    self._json_response(400, {"error": "missing_fields"})
                    return
                length_header = self.headers.get("Content-Length")
                try:
                    length = int(length_header) if length_header else 0
                except ValueError:
                    length = 0
                if length <= 0:
                    self._json_response(400, {"error": "empty_body"})
                    return
                # Cap single upload at 500 MiB
                if length > 500 * 1024 * 1024:
                    self._json_response(413, {"error": "too_large"})
                    return
                raw = self.rfile.read(length)
                digest = hashlib.sha256(raw).hexdigest()
                if digest != content_hash:
                    self._json_response(400, {"error": "hash_mismatch", "expected": content_hash, "actual": digest})
                    return

                index = server.index_for(device_id)
                existing = index.get(media_id)
                reuse = existing.filename if existing is not None else None
                if reuse and not (server.photos_dir / reuse).exists():
                    reuse = None
                force_copy = display_name_prefers_copy(display_name) and reuse is None
                ext = extension_for_mime(mime_type or None, display_name or None)
                filename = allocate_filename(
                    server.photos_dir,
                    date_taken_epoch_ms=date_taken,
                    extension=ext,
                    force_copy=force_copy,
                    reuse_filename=reuse,
                )
                dest = server.photos_dir / filename
                tmp = dest.with_suffix(dest.suffix + ".partial")
                try:
                    tmp.write_bytes(raw)
                    tmp.replace(dest)
                except OSError as exc:
                    if tmp.exists():
                        tmp.unlink(missing_ok=True)
                    server.stats.note(f"Write failed: {exc}")
                    server._notify()
                    self._json_response(500, {"error": "write_failed"})
                    return

                index.upsert(media_id, content_hash=digest, filename=filename)
                server.stats.uploads_ok += 1
                server.stats.uploads_bytes += length
                server.stats.note(f"Saved {filename}")
                server._notify()
                self._json_response(200, {"filename": filename, "status": "saved"})

            def _authorized(self, token: Any) -> bool:
                return isinstance(token, str) and secrets.compare_digest(token, server.token)

            def _read_json_body(self) -> dict[str, Any] | None:
                length_header = self.headers.get("Content-Length")
                try:
                    length = int(length_header) if length_header else 0
                except ValueError:
                    return None
                if length <= 0:
                    return {}
                if length > 20 * 1024 * 1024:
                    return None
                raw = self.rfile.read(length)
                try:
                    data = json.loads(raw.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    return None
                return data if isinstance(data, dict) else None

            def _json_response(self, status: int, payload: dict[str, Any]) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(body)

        return Handler

    def _notify(self) -> None:
        callback = self._on_change
        if callback is not None:
            try:
                callback()
            except Exception:
                logger.exception("Photo sync UI callback failed")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, photos_dir: Path, port: int = DEFAULT_PORT) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def __init__(self, photos_dir: Path, port: int = DEFAULT_PORT) -> None:
        self.photos_dir = photos_dir
        self.port = port
        self.token = secrets.token_urlsafe(18)
        self.stats = SyncStats()
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._indexes: dict[str, DeviceSyncIndex] = {}
        self._index_lock = threading.Lock()
        self._on_change: Callable[[], None] | None = None
```

</details>

### ⚙️ Method `index_for`

```python
def index_for(self, device_id: str) -> DeviceSyncIndex
```

Return (and cache) the sync index for a device.

<details>
<summary>Code:</summary>

```python
def index_for(self, device_id: str) -> DeviceSyncIndex:
        with self._index_lock:
            existing = self._indexes.get(device_id)
            if existing is not None:
                return existing
            created = DeviceSyncIndex(self.photos_dir, device_id)
            self._indexes[device_id] = created
            return created
```

</details>

### ⚙️ Method `is_running (property)`

```python
def is_running(self) -> bool
```

Whether the listener thread is active.

<details>
<summary>Code:</summary>

```python
def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
```

</details>

### ⚙️ Method `set_on_change`

```python
def set_on_change(self, callback: Callable[[], None] | None) -> None
```

Register a UI refresh callback invoked after status updates.

<details>
<summary>Code:</summary>

```python
def set_on_change(self, callback: Callable[[], None] | None) -> None:
        self._on_change = callback
```

</details>

### ⚙️ Method `start`

```python
def start(self) -> None
```

Bind and start serving in a daemon thread.

<details>
<summary>Code:</summary>

```python
def start(self) -> None:
        if self.is_running:
            return
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        handler = self._make_handler()
        try:
            self._httpd = ThreadingHTTPServer(("0.0.0.0", self.port), handler)
        except OSError:
            self.stats.note(f"Failed to bind port {self.port} (firewall or in use)")
            raise
        self._thread = threading.Thread(target=self._httpd.serve_forever, name="photo-sync-http", daemon=True)
        self._thread.start()
        self.stats.note(f"Listening on port {self.port}")
        self._notify()
```

</details>

### ⚙️ Method `stop`

```python
def stop(self) -> None
```

Stop the HTTP server.

<details>
<summary>Code:</summary>

```python
def stop(self) -> None:
        httpd = self._httpd
        self._httpd = None
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()
        thread = self._thread
        self._thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self.stats.note("Stopped")
        self._notify()
```

</details>

## 🏛️ Class `SyncStats`

```python
class SyncStats
```

Runtime counters for the listening dialog.

<details>
<summary>Code:</summary>

```python
class SyncStats:

    uploads_ok: int = 0
    uploads_bytes: int = 0
    last_message: str = ""
    log_lines: list[str] = field(default_factory=list)

    def note(self, message: str) -> None:
        """Append a short status line (keeps the last 40)."""
        self.last_message = message
        self.log_lines.append(message)
        if len(self.log_lines) > 40:
            del self.log_lines[:-40]
```

</details>

### ⚙️ Method `note`

```python
def note(self, message: str) -> None
```

Append a short status line (keeps the last 40).

<details>
<summary>Code:</summary>

```python
def note(self, message: str) -> None:
        self.last_message = message
        self.log_lines.append(message)
        if len(self.log_lines) > 40:
            del self.log_lines[:-40]
```

</details>

## 🔧 Function `get_shared_server`

```python
def get_shared_server() -> PhotoSyncServer | None
```

Return the process-wide listener, if any.

<details>
<summary>Code:</summary>

```python
def get_shared_server() -> PhotoSyncServer | None:
    with _shared_lock:
        return _shared_server
```

</details>

## 🔧 Function `set_shared_server`

```python
def set_shared_server(server: PhotoSyncServer | None) -> None
```

Install or clear the process-wide listener.

<details>
<summary>Code:</summary>

```python
def set_shared_server(server: PhotoSyncServer | None) -> None:
    global _shared_server
    with _shared_lock:
        _shared_server = server
```

</details>
