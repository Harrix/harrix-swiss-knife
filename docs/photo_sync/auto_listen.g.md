---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `auto_listen.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `attach_progress`](#-function-attach_progress)
- [🔧 Function `get_progress_controller`](#-function-get_progress_controller)
- [🔧 Function `hide_progress_toast`](#-function-hide_progress_toast)
- [🔧 Function `maybe_start_auto_listen`](#-function-maybe_start_auto_listen)
- [🔧 Function `start_shared_listener`](#-function-start_shared_listener)
- [🔧 Function `stop_shared_listener`](#-function-stop_shared_listener)

</details>

## 🔧 Function `attach_progress`

```python
def attach_progress(server: PhotoSyncServer) -> None
```

Wire transfer progress toasts to `server`.

<details>
<summary>Code:</summary>

```python
def attach_progress(server: PhotoSyncServer) -> None:
    get_progress_controller().attach(server)
```

</details>

## 🔧 Function `get_progress_controller`

```python
def get_progress_controller() -> PhotoSyncProgressController
```

Return the process-wide progress toast controller (lazy).

<details>
<summary>Code:</summary>

```python
def get_progress_controller() -> PhotoSyncProgressController:
    global _progress_controller  # noqa: PLW0603
    if _progress_controller is None:
        _progress_controller = PhotoSyncProgressController()
    return _progress_controller
```

</details>

## 🔧 Function `hide_progress_toast`

```python
def hide_progress_toast() -> None
```

Hide the transfer progress toast if shown.

<details>
<summary>Code:</summary>

```python
def hide_progress_toast() -> None:
    if _progress_controller is not None:
        _progress_controller.hide()
```

</details>

## 🔧 Function `maybe_start_auto_listen`

```python
def maybe_start_auto_listen(config: dict[str, Any]) -> bool
```

Start the shared Photo Sync server when auto-listen is fully configured.

Requires `photo_sync_auto_listen`, a valid `path_photos` folder, and saved
pairing credentials. Returns `True` when the listener is running afterward.

<details>
<summary>Code:</summary>

```python
def maybe_start_auto_listen(config: dict[str, Any]) -> bool:
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
```

</details>

## 🔧 Function `start_shared_listener`

```python
def start_shared_listener(photos_dir: Path, *, token: str | None = None, confirm_code: str | None = None, persist: bool = True, port: int = DEFAULT_PORT) -> bool
```

Create, start, and publish the shared Photo Sync server.

Returns `False` when the port cannot be bound.

<details>
<summary>Code:</summary>

```python
def start_shared_listener(
    photos_dir: Path,
    *,
    token: str | None = None,
    confirm_code: str | None = None,
    persist: bool = True,
    port: int = DEFAULT_PORT,
) -> bool:
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
```

</details>

## 🔧 Function `stop_shared_listener`

```python
def stop_shared_listener() -> None
```

Stop the shared listener and hide the progress toast.

<details>
<summary>Code:</summary>

```python
def stop_shared_listener() -> None:
    server = get_shared_server()
    if server is not None:
        get_progress_controller().detach(server)
        if server.is_running:
            server.stop()
    set_shared_server(None)
    hide_progress_toast()
```

</details>
