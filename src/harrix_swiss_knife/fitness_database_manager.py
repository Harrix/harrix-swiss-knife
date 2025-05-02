from collections import Counter
from typing import Any, Dict, Iterator, List, Optional

from PySide6.QtSql import QSqlDatabase, QSqlQuery


class FitnessDatabaseManager:
    """
    Manages the connection and operations for a fitness tracking database.

    This class provides methods to execute SQL queries, retrieve exercise data,
    and perform common database operations for a fitness application.

    Attributes:

    - `db` (`QSqlDatabase`): The SQLite database connection object.

    Raises:

    - `Exception`: If the database connection cannot be established.
    """

    def __init__(self, db_filename: str) -> None:
        """
        Initialize the database manager with a connection to the specified database file.

        Args:

        - `db_filename` (`str`): Path to the SQLite database file to open.

        Raises:

        - `Exception`: If the database connection fails.
        """
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            raise Exception("Failed to open the database")

    def _iter_query(self, query: Optional[QSqlQuery]) -> Iterator[QSqlQuery]:
        """
        Creates an iterator for SQL query results.

        Args:

        - `query` (`Optional[QSqlQuery]`): The query to iterate through.

        Returns:

        - `Iterator[QSqlQuery]`: An iterator that yields each row of the query result.
        """
        if not query:
            return
        while query.next():
            yield query

    def _rows_from_query(self, query: QSqlQuery) -> List[List]:
        """
        Extracts all rows from a query result.

        Args:

        - `query` (`QSqlQuery`): The executed query containing results.

        Returns:

        - `List[List]`: A list of rows, where each row is a list of column values.
        """
        result = []
        while query.next():
            result.append([query.value(i) for i in range(query.record().count())])
        return result

    def execute_query(self, query_text: str, params: Optional[Dict[str, Any]] = None) -> Optional[QSqlQuery]:
        """
        Prepares and executes an SQL query with optional parameter binding.

        Args:

        - `query_text` (`str`): The SQL query text to execute.
        - `params` (`Optional[Dict[str, Any]]`): Dictionary of parameters to bind to the query. Defaults to `None`.

        Returns:

        - `Optional[QSqlQuery]`: The executed query object if successful, `None` otherwise.
        """
        query = QSqlQuery()
        query.prepare(query_text)
        if params:
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        return query if query.exec() else None

    def get_exercises_by_frequency(self, limit: int = 500) -> List[str]:
        """
        Get exercises ordered by frequency of use in recent records.

        This method retrieves exercise names sorted by how frequently they appear
        in the most recent workout records.

        Args:

        - `limit` (`int`): Maximum number of recent records to analyze. Defaults to `500`.

        Returns:

        - `List[str]`: List of exercise names ordered by frequency of use.
        """
        # Get all exercises
        all_exercises = {row[0]: row[1] for row in self.get_rows("SELECT _id, name FROM exercises")}

        # Get exercise frequency from recent records
        recent_records = self.get_rows(f"SELECT _id_exercises FROM process ORDER BY _id DESC LIMIT {limit}")

        # Count frequency of each exercise
        exercise_counts = Counter(row[0] for row in recent_records)

        # Sort exercises by frequency and add any remaining exercises
        sorted_exercises = [
            all_exercises[ex_id] for ex_id, _ in exercise_counts.most_common() if ex_id in all_exercises
        ]

        # Add any remaining exercises that haven't been used recently
        return sorted_exercises + [name for _, name in all_exercises.items() if name not in sorted_exercises]

    def get_id(
        self, table: str, name_column: str, name_value: str, id_column: str = "_id", condition: Optional[str] = None
    ) -> Optional[int]:
        """
        Generic method to get an ID by name from a specified table.

        Args:

        - `table` (`str`): The table name to query.
        - `name_column` (`str`): The column containing the name to match.
        - `name_value` (`str`): The value to search for in the name column.
        - `id_column` (`str`): The column containing the ID to return. Defaults to `"_id"`.
        - `condition` (`Optional[str]`): Additional SQL WHERE conditions. Defaults to `None`.

        Returns:

        - `Optional[int]`: The ID if found, `None` otherwise.
        """
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        query_text += f" AND {condition}" if condition else ""
        params = {"name": name_value}
        query = self.execute_query(query_text, params)
        return query.value(0) if query and query.next() else None

    def get_items(
        self, table: str, column: str, condition: Optional[str] = None, order_by: Optional[str] = None
    ) -> List[Any]:
        """
        Generic method to get items from a table.

        Args:

        - `table` (`str`): The table name to query.
        - `column` (`str`): The column to retrieve values from.
        - `condition` (`Optional[str]`): Optional WHERE clause. Defaults to `None`.
        - `order_by` (`Optional[str]`): Optional ORDER BY clause. Defaults to `None`.

        Returns:

        - `List[Any]`: List of values from the specified column.
        """
        query_text = f"SELECT {column} FROM {table}"
        query_text += f" WHERE {condition}" if condition else ""
        query_text += f" ORDER BY {order_by}" if order_by else ""

        return [query.value(0) for query in self._iter_query(self.execute_query(query_text))]

    def get_rows(self, query_text: str, params: Optional[Dict[str, Any]] = None) -> List[List[Any]]:
        """
        Execute a query and return all rows as a list of lists.

        Args:

        - `query_text` (`str`): The SQL query to execute.
        - `params` (`Optional[Dict[str, Any]]`): Dictionary of parameters to bind to the query. Defaults to `None`.

        Returns:

        - `List[List[Any]]`: A list containing all rows, where each row is a list of column values.
        """
        query = self.execute_query(query_text, params)
        return self._rows_from_query(query) if query else []
