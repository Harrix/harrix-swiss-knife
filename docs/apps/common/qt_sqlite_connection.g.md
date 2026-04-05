---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_sqlite_connection.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `add_open_qsqlite`](#-function-add_open_qsqlite)
- [🔧 Function `close_and_remove_qsqlite`](#-function-close_and_remove_qsqlite)
- [🔧 Function `open_thread_scoped_qsqlite`](#-function-open_thread_scoped_qsqlite)
- [🔧 Function `qsqlite_temp_connection_name`](#-function-qsqlite_temp_connection_name)
- [🔧 Function `qsqlite_thread_scoped_connection_name`](#-function-qsqlite_thread_scoped_connection_name)
- [🔧 Function `reconnect_thread_scoped_qsqlite`](#-function-reconnect_thread_scoped_qsqlite)
- [🔧 Function `try_add_open_qsqlite`](#-function-try_add_open_qsqlite)

</details>

## 🔧 Function `add_open_qsqlite`

```python
def add_open_qsqlite(connection_name: str, db_filename: str) -> QSqlDatabase
```

Register QSQLITE, set the database file path, and open.

Raises:
ConnectionError: If the database cannot be opened. The connection is
removed from Qt's registry before raising.

<details>
<summary>Code:</summary>

```python
def add_open_qsqlite(
    connection_name: str,
    db_filename: str,
    *,
    failure_label: str = "Failed to open the database",
) -> QSqlDatabase:
    db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    db.setDatabaseName(db_filename)
    if not db.open():
        detail = db.lastError().text() if db.lastError().isValid() else "Unknown database error"
        QSqlDatabase.removeDatabase(connection_name)
        msg = f"❌ {failure_label}: {detail}"
        raise ConnectionError(msg)
    return db
```

</details>

## 🔧 Function `close_and_remove_qsqlite`

```python
def close_and_remove_qsqlite(connection_name: str | None, db: QSqlDatabase | None) -> None
```

Close `db` if it is open, then drop `connection_name` from Qt's registry.

<details>
<summary>Code:</summary>

```python
def close_and_remove_qsqlite(connection_name: str | None, db: QSqlDatabase | None) -> None:
    if db is not None and db.isValid():
        db.close()
    if connection_name:
        QSqlDatabase.removeDatabase(connection_name)
```

</details>

## 🔧 Function `open_thread_scoped_qsqlite`

```python
def open_thread_scoped_qsqlite(prefix: str, db_filename: str) -> tuple[str, QSqlDatabase]
```

Build a per-thread connection name, register QSQLITE, open, return `(name, db)`.

<details>
<summary>Code:</summary>

```python
def open_thread_scoped_qsqlite(
    prefix: str,
    db_filename: str,
    *,
    failure_label: str = "Failed to open the database",
) -> tuple[str, QSqlDatabase]:
    connection_name = qsqlite_thread_scoped_connection_name(prefix)
    database = add_open_qsqlite(connection_name, db_filename, failure_label=failure_label)
    return connection_name, database
```

</details>

## 🔧 Function `qsqlite_temp_connection_name`

```python
def qsqlite_temp_connection_name() -> str
```

Return a unique name for short-lived bootstrap or migration connections.

<details>
<summary>Code:</summary>

```python
def qsqlite_temp_connection_name() -> str:
    return f"temp_db_{uuid.uuid4().hex[:8]}"
```

</details>

## 🔧 Function `qsqlite_thread_scoped_connection_name`

```python
def qsqlite_thread_scoped_connection_name(prefix: str) -> str
```

Return a unique Qt SQL connection name for the current thread.

<details>
<summary>Code:</summary>

```python
def qsqlite_thread_scoped_connection_name(prefix: str) -> str:
    thread_id = threading.current_thread().ident
    return f"{prefix}_{uuid.uuid4().hex[:8]}_{thread_id}"
```

</details>

## 🔧 Function `reconnect_thread_scoped_qsqlite`

```python
def reconnect_thread_scoped_qsqlite() -> tuple[str, QSqlDatabase]
```

Close/remove the old Qt SQL connection and open a new thread-scoped SQLite connection.

<details>
<summary>Code:</summary>

```python
def reconnect_thread_scoped_qsqlite(
    *,
    connection_name: str | None,
    db: QSqlDatabase | None,
    prefix: str,
    db_filename: str,
    failure_label: str = "Failed to reconnect to database",
) -> tuple[str, QSqlDatabase]:
    close_and_remove_qsqlite(connection_name, db)
    return open_thread_scoped_qsqlite(prefix, db_filename, failure_label=failure_label)
```

</details>

## 🔧 Function `try_add_open_qsqlite`

```python
def try_add_open_qsqlite(connection_name: str, db_filename: str) -> tuple[QSqlDatabase | None, str | None]
```

Like `add_open_qsqlite` but return `(None, error_detail)` instead of raising.

On failure, the connection is removed from Qt's registry.

<details>
<summary>Code:</summary>

```python
def try_add_open_qsqlite(connection_name: str, db_filename: str) -> tuple[QSqlDatabase | None, str | None]:
    db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    db.setDatabaseName(db_filename)
    if not db.open():
        detail = db.lastError().text() if db.lastError().isValid() else "Unknown error"
        QSqlDatabase.removeDatabase(connection_name)
        return None, detail
    return db, None
```

</details>
