---
author: Anton Sergienko
author-email: anton.b.sergienko@gmail.com
lang: en
---

# File `fitness_database_manager.py`

<details>
<summary>📖 Contents</summary>

## Contents

- [Class `FitnessDatabaseManager`](#class-fitnessdatabasemanager)
  - [Method `__init__`](#method-__init__)
  - [Method `_iter_query`](#method-_iter_query)
  - [Method `_rows_from_query`](#method-_rows_from_query)
  - [Method `execute_query`](#method-execute_query)
  - [Method `get_exercises_by_frequency`](#method-get_exercises_by_frequency)
  - [Method `get_id`](#method-get_id)
  - [Method `get_items`](#method-get_items)
  - [Method `get_rows`](#method-get_rows)
- [Function `_safe_identifier`](#function-_safe_identifier)

</details>

## Class `FitnessDatabaseManager`

```python
class FitnessDatabaseManager
```

Manage the connection and operations for a fitness tracking database.

Attributes:

- `db` (`QSqlDatabase`): A live connection object opened on an SQLite
  database file.

<details>
<summary>Code:</summary>

```python
class FitnessDatabaseManager:

    db: QSqlDatabase

    def __init__(self, db_filename: str) -> None:
        """Open a connection to an SQLite database stored in *db_filename*.

        Args:

        - `db_filename` (`str`): The path to the target database file.

        Raises:

        - `ConnectionError`: If the underlying Qt driver fails to open the
          database.

        """
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            msg = "Failed to open the database"
            raise ConnectionError(msg)

    def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]:
        """Yield every record in *query* one by one.

        Args:

        - `query` (`Optional[QSqlQuery]`): A prepared and executed `QSqlQuery`
          object.

        Yields:

        - `QSqlQuery`: The same object positioned on consecutive records.

        """
        if query is None:
            return
        while query.next():
            yield query

    def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        """Convert the full result set in *query* into a list of rows.

        Args:

        - `query` (`QSqlQuery`): An executed query.

        Returns:

        - `List[List[Any]]`: Every database row represented as a list whose
          elements correspond to column values.

        """
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result

    def execute_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> QSqlQuery | None:
        """Prepare and execute *query_text* with optional bound *params*.

        Args:

        - `query_text` (`str`): A parametrised SQL statement.
        - `params` (`Optional[Dict[str, Any]]`): Run-time values to be bound to
          named placeholders in *query_text*. Defaults to `None`.

        Returns:

        - `Optional[QSqlQuery]`: The executed query when successful, otherwise
          `None`.

        """
        query = QSqlQuery()
        query.prepare(query_text)
        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        return query if query.exec() else None

    def get_exercises_by_frequency(self, limit: int = 500) -> list[str]:
        """Return exercise names ordered by frequency in recent *limit* rows.

        Args:

        - `limit` (`int`): Number of most recent rows from the *process* table
          to analyse. Defaults to `500`.

        Returns:

        - `List[str]`: Exercise names sorted by how often they appear; exercises
          not encountered in the inspected slice are appended afterwards.

        """
        # Validate *limit*
        if limit <= 0:
            return []

        # Full list of exercises `{id: name}`.
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Recent usage statistics.
        recent_records = self.get_rows(
            "SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT :limit",
            {"limit": limit},
        )
        exercise_counts = Counter(row[0] for row in recent_records)

        # Most common first.
        sorted_exercises = [
            all_exercises[ex_id] for ex_id, _ in exercise_counts.most_common() if ex_id in all_exercises
        ]

        # Preserve exercises not present in *sorted_exercises*.
        remainder = [name for name in all_exercises.values() if name not in sorted_exercises]
        return sorted_exercises + remainder

    def get_id(
        self,
        table: str,
        name_column: str,
        name_value: str,
        id_column: str = "_id",
        condition: str | None = None,
    ) -> int | None:
        """Return a single ID that matches *name_value* in *table*.

        Args:

        - `table` (`str`): Target table name.
        - `name_column` (`str`): Column that stores the searched value.
        - `name_value` (`str`): Searched value itself.
        - `id_column` (`str`): Column that stores the ID. Defaults to `"_id"`.
        - `condition` (`Optional[str]`): Extra SQL that will be appended to the
          `WHERE` clause. Defaults to `None`.

        Returns:

        - `int | None`: The found identifier or `None` when the query yields
          no rows.

        """
        # Validate identifiers to eliminate SQL-injection vectors.
        table = _safe_identifier(table)
        name_column = _safe_identifier(name_column)
        id_column = _safe_identifier(id_column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        if condition:
            query_text += f" AND {condition}"

        query = self.execute_query(query_text, {"name": name_value})
        return query.value(0) if query and query.next() else None

    def get_items(
        self,
        table: str,
        column: str,
        condition: str | None = None,
        order_by: str | None = None,
    ) -> list[Any]:
        """Return all values stored in *column* from *table*.

        Args:

        - `table` (`str`): Table that will be queried.
        - `column` (`str`): The column to extract.
        - `condition` (`Optional[str]`): Optional `WHERE` clause. Defaults to
          `None`.
        - `order_by` (`Optional[str]`): Optional `ORDER BY` clause. Defaults to
          `None`.

        Returns:

        - `List[Any]`: The resulting data as a flat Python list.

        """
        table = _safe_identifier(table)
        column = _safe_identifier(column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {column} FROM {table}"
        if condition:
            query_text += f" WHERE {condition}"
        if order_by:
            # The order_by expression may legitimately contain ASC/DESC or
            # multiple columns; validation is left to the caller.
            query_text += f" ORDER BY {order_by}"

        return [q.value(0) for q in self._iter_query(self.execute_query(query_text))]

    def get_rows(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        """Execute *query_text* and fetch the whole result set.

        Args:

        - `query_text` (`str`): A SQL statement.
        - `params` (`Optional[Dict[str, Any]]`): Values to be bound at run time.
          Defaults to `None`.

        Returns:

        - `List[List[Any]]`: A list whose elements are the records returned by
          the database.

        """
        query = self.execute_query(query_text, params)
        return self._rows_from_query(query) if query else []
```

</details>

### Method `__init__`

```python
def __init__(self, db_filename: str) -> None
```

Open a connection to an SQLite database stored in _db_filename_.

Args:

- `db_filename` (`str`): The path to the target database file.

Raises:

- `ConnectionError`: If the underlying Qt driver fails to open the
  database.

<details>
<summary>Code:</summary>

```python
def __init__(self, db_filename: str) -> None:
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            msg = "Failed to open the database"
            raise ConnectionError(msg)
```

</details>

### Method `_iter_query`

```python
def _iter_query(self, query: QSqlQuery | None) -> Iterator[QSqlQuery]
```

Yield every record in _query_ one by one.

Args:

- `query` (`Optional[QSqlQuery]`): A prepared and executed `QSqlQuery`
  object.

Yields:

- `QSqlQuery`: The same object positioned on consecutive records.

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

### Method `_rows_from_query`

```python
def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]
```

Convert the full result set in _query_ into a list of rows.

Args:

- `query` (`QSqlQuery`): An executed query.

Returns:

- `List[List[Any]]`: Every database row represented as a list whose
  elements correspond to column values.

<details>
<summary>Code:</summary>

```python
def _rows_from_query(self, query: QSqlQuery) -> list[list[Any]]:
        result: list[list[Any]] = []
        while query.next():
            row = [query.value(i) for i in range(query.record().count())]
            result.append(row)
        return result
```

</details>

### Method `execute_query`

```python
def execute_query(self, query_text: str, params: dict[str, Any] | None = None) -> QSqlQuery | None
```

Prepare and execute _query_text_ with optional bound _params_.

Args:

- `query_text` (`str`): A parametrised SQL statement.
- `params` (`Optional[Dict[str, Any]]`): Run-time values to be bound to
  named placeholders in _query_text_. Defaults to `None`.

Returns:

- `Optional[QSqlQuery]`: The executed query when successful, otherwise
  `None`.

<details>
<summary>Code:</summary>

```python
def execute_query(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> QSqlQuery | None:
        query = QSqlQuery()
        query.prepare(query_text)
        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        return query if query.exec() else None
```

</details>

### Method `get_exercises_by_frequency`

```python
def get_exercises_by_frequency(self, limit: int = 500) -> list[str]
```

Return exercise names ordered by frequency in recent _limit_ rows.

Args:

- `limit` (`int`): Number of most recent rows from the _process_ table
  to analyse. Defaults to `500`.

Returns:

- `List[str]`: Exercise names sorted by how often they appear; exercises
  not encountered in the inspected slice are appended afterwards.

<details>
<summary>Code:</summary>

```python
def get_exercises_by_frequency(self, limit: int = 500) -> list[str]:
        # Validate *limit*
        if limit <= 0:
            return []

        # Full list of exercises `{id: name}`.
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Recent usage statistics.
        recent_records = self.get_rows(
            "SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT :limit",
            {"limit": limit},
        )
        exercise_counts = Counter(row[0] for row in recent_records)

        # Most common first.
        sorted_exercises = [
            all_exercises[ex_id] for ex_id, _ in exercise_counts.most_common() if ex_id in all_exercises
        ]

        # Preserve exercises not present in *sorted_exercises*.
        remainder = [name for name in all_exercises.values() if name not in sorted_exercises]
        return sorted_exercises + remainder
```

</details>

### Method `get_id`

```python
def get_id(self, table: str, name_column: str, name_value: str, id_column: str = "_id", condition: str | None = None) -> int | None
```

Return a single ID that matches _name_value_ in _table_.

Args:

- `table` (`str`): Target table name.
- `name_column` (`str`): Column that stores the searched value.
- `name_value` (`str`): Searched value itself.
- `id_column` (`str`): Column that stores the ID. Defaults to `"_id"`.
- `condition` (`Optional[str]`): Extra SQL that will be appended to the
  `WHERE` clause. Defaults to `None`.

Returns:

- `int | None`: The found identifier or `None` when the query yields
  no rows.

<details>
<summary>Code:</summary>

```python
def get_id(
        self,
        table: str,
        name_column: str,
        name_value: str,
        id_column: str = "_id",
        condition: str | None = None,
    ) -> int | None:
        # Validate identifiers to eliminate SQL-injection vectors.
        table = _safe_identifier(table)
        name_column = _safe_identifier(name_column)
        id_column = _safe_identifier(id_column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        if condition:
            query_text += f" AND {condition}"

        query = self.execute_query(query_text, {"name": name_value})
        return query.value(0) if query and query.next() else None
```

</details>

### Method `get_items`

```python
def get_items(self, table: str, column: str, condition: str | None = None, order_by: str | None = None) -> list[Any]
```

Return all values stored in _column_ from _table_.

Args:

- `table` (`str`): Table that will be queried.
- `column` (`str`): The column to extract.
- `condition` (`Optional[str]`): Optional `WHERE` clause. Defaults to
  `None`.
- `order_by` (`Optional[str]`): Optional `ORDER BY` clause. Defaults to
  `None`.

Returns:

- `List[Any]`: The resulting data as a flat Python list.

<details>
<summary>Code:</summary>

```python
def get_items(
        self,
        table: str,
        column: str,
        condition: str | None = None,
        order_by: str | None = None,
    ) -> list[Any]:
        table = _safe_identifier(table)
        column = _safe_identifier(column)

        # nosec B608 - identifiers are validated by _safe_identifier
        query_text = f"SELECT {column} FROM {table}"
        if condition:
            query_text += f" WHERE {condition}"
        if order_by:
            # The order_by expression may legitimately contain ASC/DESC or
            # multiple columns; validation is left to the caller.
            query_text += f" ORDER BY {order_by}"

        return [q.value(0) for q in self._iter_query(self.execute_query(query_text))]
```

</details>

### Method `get_rows`

```python
def get_rows(self, query_text: str, params: dict[str, Any] | None = None) -> list[list[Any]]
```

Execute _query_text_ and fetch the whole result set.

Args:

- `query_text` (`str`): A SQL statement.
- `params` (`Optional[Dict[str, Any]]`): Values to be bound at run time.
  Defaults to `None`.

Returns:

- `List[List[Any]]`: A list whose elements are the records returned by
  the database.

<details>
<summary>Code:</summary>

```python
def get_rows(
        self,
        query_text: str,
        params: dict[str, Any] | None = None,
    ) -> list[list[Any]]:
        query = self.execute_query(query_text, params)
        return self._rows_from_query(query) if query else []
```

</details>

## Function `_safe_identifier`

```python
def _safe_identifier(identifier: str) -> str
```

Return _identifier_ unchanged if it is a valid SQL identifier.

The function guarantees that the returned string is composed only of
ASCII letters, digits, or underscores and does **not** start with a digit.
It is therefore safe to interpolate directly into an SQL statement.

Args:

- `identifier` (`str`): A candidate string that must be validated to be
  used as a table or column name.

Returns:

- `str`: The validated identifier (identical to the input).

Raises:

- `ValueError`: If _identifier_ contains forbidden characters.

<details>
<summary>Code:</summary>

```python
def _safe_identifier(identifier: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        msg = f"Illegal SQL identifier: {identifier!r}"
        raise ValueError(msg)
    return identifier
```

</details>
