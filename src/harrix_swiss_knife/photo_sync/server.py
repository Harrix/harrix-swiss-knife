"""HTTP receiver for LAN photo sync."""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlparse

from harrix_swiss_knife.photo_sync.durable_io import write_bytes_replacing
from harrix_swiss_knife.photo_sync.index import DeviceSyncIndex
from harrix_swiss_knife.photo_sync.lan import new_confirm_code
from harrix_swiss_knife.photo_sync.library import PhotosLibrary
from harrix_swiss_knife.photo_sync.naming import (
    allocate_filename,
    display_name_prefers_copy,
    extension_for_mime,
)

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

PROTOCOL_VERSION = 1
DEFAULT_PORT = 17865
_MAX_LOG_LINES = 40
_MAX_UPLOAD_BYTES = 500 * 1024 * 1024
_MAX_JSON_BODY_BYTES = 20 * 1024 * 1024


@dataclass
class PhoneConnectionInfo:
    """Last observed activity from a paired Android device."""

    device_id: str = ""
    last_at: float | None = None
    last_event: str = ""


class PhotoSyncServer:
    """Tokenized LAN HTTP server that receives photos into `photos_dir`."""

    def __init__(
        self,
        photos_dir: Path,
        port: int = DEFAULT_PORT,
        *,
        token: str | None = None,
        confirm_code: str | None = None,
    ) -> None:
        """Create a stopped server that will write into `photos_dir`.

        When `token` / `confirm_code` are provided (and non-empty), they are reused
        so a phone that already paired can reconnect after an app restart.

        """
        self.photos_dir = photos_dir
        self.port = port
        cleaned_token = (token or "").strip()
        cleaned_code = (confirm_code or "").strip()
        self.token = cleaned_token or secrets.token_urlsafe(18)
        # Shown on the PC next to the QR; phone must pick the matching number.
        self.confirm_code = cleaned_code or new_confirm_code()
        self.stats = SyncStats()
        self.library = PhotosLibrary(photos_dir)
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
        removed_partials = _cleanup_partial_files(self.photos_dir)
        handler = self._make_handler()
        try:
            # Bind all interfaces so phones on LAN can connect.
            self._httpd = ThreadingHTTPServer(("0.0.0.0", self.port), handler)  # noqa: S104
        except OSError:
            self.stats.note(f"Failed to bind port {self.port} (firewall or in use)")
            raise
        self._thread = threading.Thread(target=self._httpd.serve_forever, name="photo-sync-http", daemon=True)
        self._thread.start()
        if removed_partials:
            self.stats.note(f"Removed {removed_partials} incomplete .partial file(s)")
        self.stats.note(f"Listening on port {self.port}")
        self.stats.note("Indexing photo library in background…")
        self._notify()

        def _on_library_warm() -> None:
            self.stats.note(f"Photo library ready ({self.library.unique_hash_count} unique hashes)")
            self._notify()

        self.library.warm_in_background(on_done=_on_library_warm)

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

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
                logger.debug("photo-sync: %s", format % args)

            def do_GET(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path == "/v1/health":
                    self._json_response(200, {"ok": True, "protocolVersion": PROTOCOL_VERSION})
                    return
                self._json_response(404, {"error": "not_found"})

            def do_POST(self) -> None:
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

            def do_PUT(self) -> None:
                parsed = urlparse(self.path)
                if parsed.path != "/v1/upload":
                    self._json_response(404, {"error": "not_found"})
                    return
                self._handle_upload(parsed)

            def _handle_handshake(self, body: dict[str, Any]) -> None:
                if not self._authorized(body.get("token")):
                    self._json_response(401, {"error": "unauthorized"})
                    return
                if not self._confirm_ok(body.get("confirmCode")):
                    self._json_response(403, {"error": "confirm_code_mismatch"})
                    return
                device_id = str(body.get("deviceId", "")).strip()
                if not device_id:
                    self._json_response(400, {"error": "device_id_required"})
                    return
                server.stats.record_phone(device_id, "handshake")
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
                server.stats.record_phone(device_id, "manifest")
                server.stats.note("Checking photo library for existing files…")
                server._notify()
                # Prefer a recent/warm index; full rescan of Dropbox can exceed phone timeouts.
                server.library.ensure_fresh()
                needed = index.needed_media_ids(
                    items,
                    find_existing_hash=server.library.find_relative_path,
                )
                server.stats.begin_session(len(needed))
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
                server.stats.record_phone(device_id, "upload")
                length_header = self.headers.get("Content-Length")
                try:
                    length = int(length_header) if length_header else 0
                except ValueError:
                    length = 0
                if length <= 0:
                    self._json_response(400, {"error": "empty_body"})
                    return
                if length > _MAX_UPLOAD_BYTES:
                    self._json_response(413, {"error": "too_large"})
                    return
                try:
                    raw = self.rfile.read(length)
                except (ConnectionError, BrokenPipeError, TimeoutError, OSError) as exc:
                    server.stats.note(f"Upload interrupted: {exc}")
                    server._notify()
                    return
                if len(raw) != length:
                    # Incomplete body: do not index; phone will retry next sync.
                    server.stats.note(f"Incomplete upload for mediaId={media_id} ({len(raw)}/{length})")
                    server._notify()
                    self._json_response(400, {"error": "incomplete_body"})
                    return
                digest = hashlib.sha256(raw).hexdigest()
                if digest != content_hash:
                    self._json_response(400, {"error": "hash_mismatch", "expected": content_hash, "actual": digest})
                    return

                index = server.index_for(device_id)
                existing = index.get(media_id)
                reuse = existing.filename if existing is not None else None
                if reuse and not (server.photos_dir / reuse).is_file():
                    reuse = None
                # Already present in a sorted subfolder (race / late library hit).
                existing_path = server.library.find_relative_path(digest)
                if existing_path and reuse is None:
                    index.upsert(media_id, content_hash=digest, filename=existing_path)
                    server.stats.note(f"Skipped (already in library): {existing_path}")
                    server.stats.record_session_item()
                    server._notify()
                    self._json_response(200, {"filename": existing_path, "status": "exists"})
                    return
                force_copy = display_name_prefers_copy(display_name) and reuse is None
                ext = extension_for_mime(mime_type or None, display_name or None)
                filename = allocate_filename(
                    server.photos_dir,
                    date_taken_epoch_ms=date_taken,
                    extension=ext,
                    force_copy=force_copy,
                    reuse_filename=reuse,
                )
                dest = _safe_dest(server.photos_dir, filename)
                if dest is None:
                    self._json_response(400, {"error": "invalid_path"})
                    return
                try:
                    write_bytes_replacing(dest, raw, tmp_suffix=".partial")
                except OSError as exc:
                    server.stats.note(f"Write failed: {exc}")
                    server._notify()
                    self._json_response(500, {"error": "write_failed"})
                    return

                # Index only after the final file is in place (never for .partial).
                try:
                    index.upsert(media_id, content_hash=digest, filename=filename)
                except OSError as exc:
                    # Photo is already on disk; still report success so the phone
                    # does not re-upload under a `_copy` name on the next sync.
                    server.stats.note(f"Saved {filename}; index update failed: {exc}")
                else:
                    server.stats.note(f"Saved {filename}")
                server.library.remember(filename, digest)
                server.stats.uploads_ok += 1
                server.stats.uploads_bytes += length
                server.stats.record_session_item()
                server._notify()
                self._json_response(200, {"filename": filename, "status": "saved"})

            def _authorized(self, token: Any) -> bool:
                return isinstance(token, str) and secrets.compare_digest(token, server.token)

            def _confirm_ok(self, confirm_code: Any) -> bool:
                if not isinstance(confirm_code, str):
                    return False
                return secrets.compare_digest(confirm_code.strip(), server.confirm_code)

            def _read_json_body(self) -> dict[str, Any] | None:
                length_header = self.headers.get("Content-Length")
                try:
                    length = int(length_header) if length_header else 0
                except ValueError:
                    return None
                if length <= 0:
                    return {}
                if length > _MAX_JSON_BODY_BYTES:
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


@dataclass
class SyncStats:
    """Runtime counters for the listening dialog and transfer toast."""

    uploads_ok: int = 0
    uploads_bytes: int = 0
    last_message: str = ""
    log_lines: list[str] = field(default_factory=list)
    last_phone_device_id: str = ""
    last_phone_at: float | None = None
    last_phone_event: str = ""
    session_total: int = 0
    session_done: int = 0
    session_active: bool = False

    def begin_session(self, total: int) -> None:
        """Start a transfer session from a manifest `needed` count."""
        count = max(0, int(total))
        self.session_total = count
        self.session_done = 0
        self.session_active = count > 0

    def end_session(self) -> None:
        """Mark the current transfer session as inactive."""
        self.session_active = False

    def note(self, message: str) -> None:
        """Append a short status line (keeps the last `_MAX_LOG_LINES`)."""
        self.last_message = message
        self.log_lines.append(message)
        if len(self.log_lines) > _MAX_LOG_LINES:
            del self.log_lines[:-_MAX_LOG_LINES]

    def record_phone(self, device_id: str, event: str) -> None:
        """Remember phone activity for the settings / status UI."""
        self.last_phone_device_id = device_id
        self.last_phone_at = time.time()
        self.last_phone_event = event
        remember_phone_activity(device_id, event)

    def record_session_item(self) -> None:
        """Count one finished upload (or library hit) toward the open session."""
        if self.session_total <= 0:
            return
        self.session_done = min(self.session_done + 1, self.session_total)
        if self.session_done >= self.session_total:
            self.session_active = False

    @property
    def session_in_progress(self) -> bool:
        """`True` while a transfer batch has remaining items (or just started)."""
        return self.session_total > 0 and self.session_done < self.session_total


class _SharedServerState:
    """Process-wide listener holder (avoids a module-level `global` assignment)."""

    def __init__(self) -> None:
        """Create an empty shared holder."""
        self.lock = threading.Lock()
        self.server: PhotoSyncServer | None = None
        self.phone = PhoneConnectionInfo()


def get_phone_connection_info() -> PhoneConnectionInfo:
    """Return a copy of the last phone activity seen this process lifetime."""
    with _SHARED.lock:
        phone = _SHARED.phone
        return PhoneConnectionInfo(
            device_id=phone.device_id,
            last_at=phone.last_at,
            last_event=phone.last_event,
        )


def get_shared_server() -> PhotoSyncServer | None:
    """Return the process-wide listener, if any."""
    with _SHARED.lock:
        return _SHARED.server


def remember_phone_activity(device_id: str, event: str) -> None:
    """Persist last phone activity across listen stop/start in this process."""
    with _SHARED.lock:
        _SHARED.phone.device_id = device_id
        _SHARED.phone.last_at = time.time()
        _SHARED.phone.last_event = event


def set_shared_server(server: PhotoSyncServer | None) -> None:
    """Install or clear the process-wide listener."""
    with _SHARED.lock:
        _SHARED.server = server


def _cleanup_partial_files(photos_dir: Path) -> int:
    """Delete leftover `*.partial` files from interrupted uploads."""
    if not photos_dir.is_dir():
        return 0
    removed = 0
    for path in photos_dir.rglob("*.partial"):
        if not path.is_file():
            continue
        try:
            path.unlink()
            removed += 1
        except OSError:
            continue
    return removed


def _safe_dest(photos_dir: Path, relative_path: str) -> Path | None:
    """Resolve `relative_path` under `photos_dir`, rejecting path escape."""
    relative = relative_path.replace("\\", "/").lstrip("/")
    if not relative or ".." in Path(relative).parts:
        return None
    root = photos_dir.resolve()
    dest = (photos_dir / relative).resolve()
    try:
        dest.relative_to(root)
    except ValueError:
        return None
    return dest


_SHARED = _SharedServerState()
