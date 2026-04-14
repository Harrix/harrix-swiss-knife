---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# 📄 File `qt_sql_runner.py`

<details>
<summary>📖 Contents ⬇️</summary>

## Contents

- [🔧 Function `execute_qt_sql_query`](#-function-execute_qt_sql_query)
- [🔧 Function `execute_qt_sql_simple`](#-function-execute_qt_sql_simple)

</details>

## 🔧 Function `execute_qt_sql_query`

```python
def execute_qt_sql_query() -> QSqlQuery | None
```

Prepare and execute `query_text` with optional bound `params`.

Args:

- `ensure_connection`: Return whether the database connection is usable.
- `create_query`: Build a `QSqlQuery` bound to the open connection.
- `query_text`: Parametrised SQL statement.
- `params`: Values for named placeholders. Defaults to `None`.

Returns:

- `QSqlQuery | None`: The executed query when successful, otherwise `None`.

<details>
<summary>Code:</summary>

```python
def execute_qt_sql_query(
    *,
    ensure_connection: Callable[[], bool],
    create_query: Callable[[], QSqlQuery],
    query_text: str,
    params: dict[str, Any] | None = None,
) -> QSqlQuery | None:
    if not ensure_connection():
        logger.error("Database connection is not available for query execution")
        return None

    try:
        query = create_query()
        if not query.prepare(query_text):
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
            logger.error("Failed to prepare Qt SQL query: %s", error_msg)
            return None

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        if not query.exec():
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
            logger.error("Failed to execute Qt SQL query: %s", error_msg)
            return None

    except Exception:
        logger.exception("Exception during Qt SQL query execution")
        return None

    else:
        return query
```

</details>

## 🔧 Function `execute_qt_sql_simple`

```python
def execute_qt_sql_simple() -> bool
```

Execute INSERT/UPDATE/DELETE and return success; clear query on success.

Args:

- `ensure_connection`: Return whether the database connection is usable.
- `create_query`: Build a `QSqlQuery` bound to the open connection.
- `query_text`: Parametrised SQL statement.
- `params`: Values for named placeholders. Defaults to `None`.

Returns:

- `bool`: `True` if successful, `False` otherwise.

<details>
<summary>Code:</summary>

```python
def execute_qt_sql_simple(
    *,
    ensure_connection: Callable[[], bool],
    create_query: Callable[[], QSqlQuery],
    query_text: str,
    params: dict[str, Any] | None = None,
) -> bool:
    if not ensure_connection():
        logger.error("Database connection is not available for query execution")
        return False

    try:
        query = create_query()
        if not query.prepare(query_text):
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown prepare error"
            logger.error("Failed to prepare Qt SQL query: %s", error_msg)
            return False

        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)

        success = query.exec()
        if not success:
            error_msg = query.lastError().text() if query.lastError().isValid() else "Unknown execution error"
            logger.error("Failed to execute Qt SQL query: %s", error_msg)
            return False

    except Exception:
        logger.exception("Exception during Qt SQL query execution")
        return False

    else:
        query.clear()
        return True
```

</details>
