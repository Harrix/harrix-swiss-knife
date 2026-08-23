---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `single_instance.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `SingleInstance`](#%EF%B8%8F-class-singleinstance)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
  - [⚙️ Method `release`](#%EF%B8%8F-method-release)
  - [⚙️ Method `try_claim`](#%EF%B8%8F-method-try_claim)
- [🔧 Function `acquire_tray_instance`](#-function-acquire_tray_instance)
- [🔧 Function `default_server_name`](#-function-default_server_name)
- [🔧 Function `release_held_instance`](#-function-release_held_instance)
- [🔧 Function `restore_held_instance`](#-function-restore_held_instance)

</details>

## 🏛️ Class `SingleInstance`

```python
class SingleInstance(QObject)
```

Listen for (or notify) another tray process on a per-user local socket.

<details>
<summary>Code:</summary>

```python
class SingleInstance(QObject):

    activate_requested = Signal()

    def __init__(self, name: str | None = None, parent: QObject | None = None) -> None:
        """Create a guard for `name` (defaults to a per-user Swiss Knife socket)."""
        super().__init__(parent)
        self._name = name or default_server_name()
        self._server: QLocalServer | None = None

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
            payload = bytes(socket.readAll().data())
            if _ACTIVATE_MESSAGE.strip() in payload:
                self.activate_requested.emit()
            socket.disconnectFromServer()

        socket.readyRead.connect(_read)
        if socket.bytesAvailable():
            _read()
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self, name: str | None = None, parent: QObject | None = None) -> None
```

Create a guard for `name` (defaults to a per-user Swiss Knife socket).

<details>
<summary>Code:</summary>

```python
def __init__(self, name: str | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._name = name or default_server_name()
        self._server: QLocalServer | None = None
```

</details>

### ⚙️ Method `release`

```python
def release(self) -> None
```

Close the listener so another process can become primary.

<details>
<summary>Code:</summary>

```python
def release(self) -> None:
        server = self._server
        self._server = None
        if server is None:
            return
        server.close()
        QLocalServer.removeServer(self._name)
```

</details>

### ⚙️ Method `try_claim`

```python
def try_claim(self) -> bool
```

Become the primary instance, or notify the existing one.

Returns:

- `bool`: `True` when this process should keep running. `False` when
  another instance is already running and was asked to show the window.

<details>
<summary>Code:</summary>

```python
def try_claim(self) -> bool:
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
```

</details>

## 🔧 Function `acquire_tray_instance`

```python
def acquire_tray_instance(on_activate: Callable[[], None], *, name: str | None = None) -> SingleInstance | None
```

Claim the tray singleton. Return the guard, or `None` when another instance owns it.

<details>
<summary>Code:</summary>

```python
def acquire_tray_instance(on_activate: Callable[[], None], *, name: str | None = None) -> SingleInstance | None:
    global _held  # noqa: PLW0603
    instance = SingleInstance(name=name)
    instance.activate_requested.connect(on_activate)
    if not instance.try_claim():
        instance.deleteLater()
        return None
    _held = instance
    return instance
```

</details>

## 🔧 Function `default_server_name`

```python
def default_server_name() -> str
```

Return a per-user local-socket name for the tray app.

<details>
<summary>Code:</summary>

```python
def default_server_name() -> str:
    raw = os.environ.get("USERNAME") or os.environ.get("USER") or getpass.getuser()
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in raw)
    return f"harrix-swiss-knife-{safe or 'user'}"
```

</details>

## 🔧 Function `release_held_instance`

```python
def release_held_instance() -> SingleInstance | None
```

Release the process-wide tray singleton (used before restart).

<details>
<summary>Code:</summary>

```python
def release_held_instance() -> SingleInstance | None:
    global _held  # noqa: PLW0603
    instance = _held
    _held = None
    if instance is not None:
        instance.release()
    return instance
```

</details>

## 🔧 Function `restore_held_instance`

```python
def restore_held_instance(instance: SingleInstance) -> bool
```

Become primary again after a failed restart spawn.

Returns:

- `bool`: `True` when this process reclaimed the socket.

<details>
<summary>Code:</summary>

```python
def restore_held_instance(instance: SingleInstance) -> bool:
    global _held  # noqa: PLW0603
    if not instance.try_claim():
        return False
    _held = instance
    return True
```

</details>
