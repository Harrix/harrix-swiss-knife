---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_database_manager_base.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🏛️ Class `DatabaseConnectionUnavailableError`](#%EF%B8%8F-class-databaseconnectionunavailableerror)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__)
- [🏛️ Class `QtSqliteDatabaseManagerBase`](#%EF%B8%8F-class-qtsqlitedatabasemanagerbase)
  - [⚙️ Method `__init__`](#%EF%B8%8F-method-__init__-1)
  - [⚙️ Method `close`](#%EF%B8%8F-method-close)
  - [⚙️ Method `create_database_from_sql`](#%EF%B8%8F-method-create_database_from_sql)
  - [⚙️ Method `execute_query`](#%EF%B8%8F-method-execute_query)
  - [⚙️ Method `execute_simple_query`](#%EF%B8%8F-method-execute_simple_query)
  - [⚙️ Method `get_rows`](#%EF%B8%8F-method-get_rows)
  - [⚙️ Method `is_database_open`](#%EF%B8%8F-method-is_database_open)
  - [⚙️ Method `rows_from_query`](#%EF%B8%8F-method-rows_from_query)
  - [⚙️ Method `table_exists`](#%EF%B8%8F-method-table_exists)
  - [⚙️ Method `_create_query`](#%EF%B8%8F-method-_create_query)
  - [⚙️ Method `_ensure_connection`](#%EF%B8%8F-method-_ensure_connection)
  - [⚙️ Method `_iter_query`](#%EF%B8%8F-method-_iter_query)
  - [⚙️ Method `_reconnect`](#%EF%B8%8F-method-_reconnect)

</details>

## 🏛️ Class `DatabaseConnectionUnavailableError`

```python
class DatabaseConnectionUnavailableError(ConnectionError)
```

Database connection is not available.

<details>
<summary>Code:</summary>

```python
class DatabaseConnectionUnavailableError(ConnectionError):

    def __init__(self) -> None:
        """Create exception with standard message."""
        super().__init__("❌ Database connection is not available")
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create exception with standard message.

<details>
<summary>Code:</summary>

```python
def __init__(self) -> None:
        super().__init__("❌ Database connection is not available")
```

</details>

## 🏛️ Class `QtSqliteDatabaseManagerBase`

```python
class QtSqliteDatabaseManagerBase
```

Base class that manages a thread-scoped Qt SQLite connection.

<details>
<summary>Code:</summary>

```python
class QtSqliteDatabaseManagerBase:

    db: QSqlDatabase | None
    connection_name: str

    _db_filename: str
    _connection_prefix: str
    _db_closed: bool

    def __init__(self, *, prefix: str, db_filename: str) -> None:
        """Create manager bound to `db_filename` for the current thread."""
        self._connection_prefix = prefix
        self._db_filename = db_filename
        self.connection_name, self.db = open_thread_scoped_qsqlite(prefix, db_filename)
        self._db_closed = False

    def close(self) -> None:
        """Close the database connection and remove it from Qt registry."""
        if self._db_closed:
            return
        self._db_closed = True
        connection_name = self.connection_name
        db = getattr(self, "db", None)
        if db is not None and db.isValid():
            db.close()
        self.db = None
        QTimer.singleShot(0, lambda n=connection_name: QSqlDatabase.removeDatabase(n))

    @staticmethod
    def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool:
        """Create a new database from an SQL file."""
        try:
            db_path = Path(db_filename)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            sql_path = Path(sql_file_path)
            if not sql_path.exists():
                logger.error("SQL file not found: %s", sql_file_path)
                return False

            sql_content = sql_path.read_text(encoding="utf-8")

            temp_connection_name = qsqlite_temp_connection_name()
            temp_db, open_err = try_add_open_qsqlite(temp_connection_name, db_filename)
            if open_err is not None or temp_db is None:
                logger.error("Failed to create database: %s", open_err or "Unknown error")
                return False

            try:
                query = QSqlQuery(temp_db)
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for statement in statements:
                    if not query.exec(statement):
                        error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown error"
                        logger.error("Failed to execute SQL statement: %s", error_msg)
                        return False

                logger.info("Database created successfully: %s", db_filename)
                return True
            finally:
                temp_db.close()
                QSqlDatabase.removeDatabase(temp_connection_name)
        except Exception:
            logger.exception("Error creating database from SQL file")
            return False

    def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None:
        """Prepare and execute `query_text` with optional bound `params`."""
        return execute_qt_sql_query(
            ensure_connection=self._ensure_connection,
            create_query=self._create_query,
            query_text=query_text,
            params=params,
        )

    def execute_simple_query(self, query_text: str, params: dict[str, Any] | None = None) -> bool:
        """Execute INSERT/UPDATE/DELETE and return success status."""
        return execute_qt_sql_simple(
            ensure_connection=self._ensure_connection,
            create_query=self._create_query,
            query_text=query_text,
            params=params,
        )

    def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]:
        """Execute `query_text` and fetch the full result set."""
        query = self.execute_query(query_text, params)
        if query:
            result = self.rows_from_query(query)
            query.clear()
            return result
        return []

    def is_database_open(self) -> bool:
        """Return whether Qt connection is open and valid."""
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()

    def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        """Convert the full result set in `query` into a list of rows."""
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        if not self.is_database_open():
            return False
        query = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name",
            {"table_name": table_name},
        )
        return bool(query and query.next())

    def _create_query(self) -> QSqlQuery:
        if not self._ensure_connection() or self.db is None:
            raise DatabaseConnectionUnavailableError
        return QSqlQuery(self.db)

    def _ensure_connection(self) -> bool:
        if not hasattr(self, "db") or self.db is None or not self.db.isValid():
            logger.warning("Database object is invalid, attempting to reconnect")
            try:
                self._reconnect()
                return self.db is not None and self.db.isOpen()
            except Exception:
                logger.exception("Failed to reconnect to database")
                return False

        if self.db is None or not self.db.isOpen():
            logger.warning("Database connection is closed, attempting to reopen")
            if self.db is None or not self.db.open():
                error_msg = self.db.lastError().text() if self.db and self.db.lastError().isValid() else "Unknown error"
                logger.error("Failed to reopen database: %s", error_msg)
                try:
                    self._reconnect()
                    return self.db is not None and self.db.isOpen()
                except Exception:
                    logger.exception("Failed to reconnect to database")
                    return False

        return True

    def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        if query is None:
            return
        while query.next():
            yield query

    def _reconnect(self) -> None:
        self.connection_name, self.db = reconnect_thread_scoped_qsqlite(
            connection_name=self.connection_name,
            db=self.db,
            prefix=self._connection_prefix,
            db_filename=self._db_filename,
        )
        self._db_closed = False
```

</details>

### ⚙️ Method `__init__`

```python
def __init__(self) -> None
```

Create manager bound to `db_filename` for the current thread.

<details>
<summary>Code:</summary>

```python
def __init__(self, *, prefix: str, db_filename: str) -> None:
        self._connection_prefix = prefix
        self._db_filename = db_filename
        self.connection_name, self.db = open_thread_scoped_qsqlite(prefix, db_filename)
        self._db_closed = False
```

</details>

### ⚙️ Method `close`

```python
def close(self) -> None
```

Close the database connection and remove it from Qt registry.

<details>
<summary>Code:</summary>

```python
def close(self) -> None:
        if self._db_closed:
            return
        self._db_closed = True
        connection_name = self.connection_name
        db = getattr(self, "db", None)
        if db is not None and db.isValid():
            db.close()
        self.db = None
        QTimer.singleShot(0, lambda n=connection_name: QSqlDatabase.removeDatabase(n))
```

</details>

### ⚙️ Method `create_database_from_sql`

```python
def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool
```

Create a new database from an SQL file.

<details>
<summary>Code:</summary>

```python
def create_database_from_sql(db_filename: str, sql_file_path: str) -> bool:
        try:
            db_path = Path(db_filename)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            sql_path = Path(sql_file_path)
            if not sql_path.exists():
                logger.error("SQL file not found: %s", sql_file_path)
                return False

            sql_content = sql_path.read_text(encoding="utf-8")

            temp_connection_name = qsqlite_temp_connection_name()
            temp_db, open_err = try_add_open_qsqlite(temp_connection_name, db_filename)
            if open_err is not None or temp_db is None:
                logger.error("Failed to create database: %s", open_err or "Unknown error")
                return False

            try:
                query = QSqlQuery(temp_db)
                statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]
                for statement in statements:
                    if not query.exec(statement):
                        error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown error"
                        logger.error("Failed to execute SQL statement: %s", error_msg)
                        return False

                logger.info("Database created successfully: %s", db_filename)
                return True
            finally:
                temp_db.close()
                QSqlDatabase.removeDatabase(temp_connection_name)
        except Exception:
            logger.exception("Error creating database from SQL file")
            return False
```

</details>

### ⚙️ Method `execute_query`

```python
def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None
```

Prepare and execute `query_text` with optional bound `params`.

<details>
<summary>Code:</summary>

```python
def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None:
        return execute_qt_sql_query(
            ensure_connection=self._ensure_connection,
            create_query=self._create_query,
            query_text=query_text,
            params=params,
        )
```

</details>

### ⚙️ Method `execute_simple_query`

```python
def execute_simple_query(self, query_text: str, params: dict[str, Any] | None = None) -> bool
```

Execute INSERT/UPDATE/DELETE and return success status.

<details>
<summary>Code:</summary>

```python
def execute_simple_query(self, query_text: str, params: dict[str, Any] | None = None) -> bool:
        return execute_qt_sql_simple(
            ensure_connection=self._ensure_connection,
            create_query=self._create_query,
            query_text=query_text,
            params=params,
        )
```

</details>

### ⚙️ Method `get_rows`

```python
def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]
```

Execute `query_text` and fetch the full result set.

<details>
<summary>Code:</summary>

```python
def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]:
        query = self.execute_query(query_text, params)
        if query:
            result = self.rows_from_query(query)
            query.clear()
            return result
        return []
```

</details>

### ⚙️ Method `is_database_open`

```python
def is_database_open(self) -> bool
```

Return whether Qt connection is open and valid.

<details>
<summary>Code:</summary>

```python
def is_database_open(self) -> bool:
        return hasattr(self, "db") and self.db is not None and self.db.isValid() and self.db.isOpen()
```

</details>

### ⚙️ Method `rows_from_query`

```python
def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]
```

Convert the full result set in `query` into a list of rows.

<details>
<summary>Code:</summary>

```python
def rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result
```

</details>

### ⚙️ Method `table_exists`

```python
def table_exists(self, table_name: str) -> bool
```

Check if a table exists in the database.

<details>
<summary>Code:</summary>

```python
def table_exists(self, table_name: str) -> bool:
        if not self.is_database_open():
            return False
        query = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:table_name",
            {"table_name": table_name},
        )
        return bool(query and query.next())
```

</details>

### ⚙️ Method `_create_query`

```python
def _create_query(self) -> QSqlQuery
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _create_query(self) -> QSqlQuery:
        if not self._ensure_connection() or self.db is None:
            raise DatabaseConnectionUnavailableError
        return QSqlQuery(self.db)
```

</details>

### ⚙️ Method `_ensure_connection`

```python
def _ensure_connection(self) -> bool
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _ensure_connection(self) -> bool:
        if not hasattr(self, "db") or self.db is None or not self.db.isValid():
            logger.warning("Database object is invalid, attempting to reconnect")
            try:
                self._reconnect()
                return self.db is not None and self.db.isOpen()
            except Exception:
                logger.exception("Failed to reconnect to database")
                return False

        if self.db is None or not self.db.isOpen():
            logger.warning("Database connection is closed, attempting to reopen")
            if self.db is None or not self.db.open():
                error_msg = self.db.lastError().text() if self.db and self.db.lastError().isValid() else "Unknown error"
                logger.error("Failed to reopen database: %s", error_msg)
                try:
                    self._reconnect()
                    return self.db is not None and self.db.isOpen()
                except Exception:
                    logger.exception("Failed to reconnect to database")
                    return False

        return True
```

</details>

### ⚙️ Method `_iter_query`

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        if query is None:
            return
        while query.next():
            yield query
```

</details>

### ⚙️ Method `_reconnect`

```python
def _reconnect(self) -> None
```

_No docstring provided._

<details>
<summary>Code:</summary>

```python
def _reconnect(self) -> None:
        self.connection_name, self.db = reconnect_thread_scoped_qsqlite(
            connection_name=self.connection_name,
            db=self.db,
            prefix=self._connection_prefix,
            db_filename=self._db_filename,
        )
        self._db_closed = False
```

</details>
