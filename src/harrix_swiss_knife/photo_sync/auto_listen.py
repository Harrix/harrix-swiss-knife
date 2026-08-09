"""Background Photo Sync listener started from app startup."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from harrix_swiss_knife.paths import get_config_path_str
from harrix_swiss_knife.photo_sync.progress_toast import PhotoSyncProgressController
from harrix_swiss_knife.photo_sync.server import (
    DEFAULT_PORT,
    PhotoSyncServer,
    get_shared_server,
    set_shared_server,
)
from harrix_swiss_knife.photo_sync.settings import (
    is_auto_listen_enabled,
    load_saved_credentials,
    persist_credentials,
    photos_dir_from_config,
)

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

_progress_controller: PhotoSyncProgressController | None = None


def attach_progress(server: PhotoSyncServer) -> None:
    """Wire transfer progress toasts to `server`."""
    get_progress_controller().attach(server)


def get_progress_controller() -> PhotoSyncProgressController:
    """Return the process-wide progress toast controller (lazy)."""
    global _progress_controller  # noqa: PLW0603
    if _progress_controller is None:
        _progress_controller = PhotoSyncProgressController()
    return _progress_controller


def hide_progress_toast() -> None:
    """Hide the transfer progress toast if shown."""
    if _progress_controller is not None:
        _progress_controller.hide()


def maybe_start_auto_listen(config: dict[str, Any]) -> bool:
    """Start the shared Photo Sync server when auto-listen is fully configured.

    Requires `photo_sync_auto_listen`, a valid `path_photos` folder, and saved
    pairing credentials. Returns `True` when the listener is running afterward.

    """
    if not is_auto_listen_enabled(config):
        return False
    existing = get_shared_server()
    if existing is not None and existing.is_running:
        attach_progress(existing)
        return True
    photos_dir = photos_dir_from_config(config)
    if photos_dir is None:
        logger.info("Photo sync auto-listen skipped: path_photos missing or not a folder")
        return False
    credentials = load_saved_credentials(config)
    if credentials is None:
        logger.info("Photo sync auto-listen skipped: pair once via Photo sync dialog first")
        return False
    token, confirm_code = credentials
    return start_shared_listener(
        photos_dir,
        token=token,
        confirm_code=confirm_code,
        persist=True,
    )


def start_shared_listener(
    photos_dir: Path,
    *,
    token: str | None = None,
    confirm_code: str | None = None,
    persist: bool = True,
    port: int = DEFAULT_PORT,
) -> bool:
    """Create, start, and publish the shared Photo Sync server.

    Returns `False` when the port cannot be bound.

    """
    existing = get_shared_server()
    if existing is not None and existing.is_running:
        attach_progress(existing)
        return True
    server = PhotoSyncServer(
        photos_dir,
        port=port,
        token=token,
        confirm_code=confirm_code,
    )
    try:
        server.start()
    except OSError:
        logger.exception("Photo sync auto-listen failed to bind port %s", port)
        return False
    set_shared_server(server)
    attach_progress(server)
    if persist:
        persist_credentials(
            get_config_path_str(),
            token=server.token,
            confirm_code=server.confirm_code,
        )
    logger.info("Photo sync listening on port %s (auto-listen)", port)
    return True


def stop_shared_listener() -> None:
    """Stop the shared listener and hide the progress toast."""
    server = get_shared_server()
    if server is not None:
        get_progress_controller().detach(server)
        if server.is_running:
            server.stop()
    set_shared_server(None)
    hide_progress_toast()
