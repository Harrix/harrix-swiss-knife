from collections import Counter

from PySide6.QtSql import QSqlDatabase, QSqlQuery

class FitnessDatabaseManager:
    def __init__(self, db_filename):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_filename)
        if not self.db.open():
            raise Exception("Failed to open the database")

    def _iter_query(self, query):
        """Iterator for query results"""
        if not query:
            return
        while query.next():
            yield query

    def _rows_from_query(self, query):
        """Extract all rows from a query result"""
        result = []
        while query.next():
            result.append([query.value(i) for i in range(query.record().count())])
        return result

    def execute_query(self, query_text, params=None):
        query = QSqlQuery()
        if params:
            query.prepare(query_text)
            for key, value in params.items():
                query.bindValue(f":{key}", value)
        else:
            query.prepare(query_text)
        return query if query.exec() else None

    def get_exercises_by_frequency(self, limit=500):
        """Get exercises ordered by frequency of use in recent records"""
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
        return sorted_exercises + [name for ex_id, name in all_exercises.items() if name not in sorted_exercises]

    def get_id(self, table, name_column, name_value, id_column="_id", condition=None):
        """Generic method to get ID by name"""
        query_text = f"SELECT {id_column} FROM {table} WHERE {name_column} = :name"
        query_text += f" AND {condition}" if condition else ""
        params = {"name": name_value}
        query = self.execute_query(query_text, params)
        return query.value(0) if query and query.next() else None

    def get_items(self, table, column, condition=None, order_by=None):
        """Generic method to get items from a table"""
        query_text = f"SELECT {column} FROM {table}"
        query_text += f" WHERE {condition}" if condition else ""
        query_text += f" ORDER BY {order_by}" if order_by else ""

        return [query.value(0) for query in self._iter_query(self.execute_query(query_text))]

    def get_rows(self, query_text, params=None):
        """Execute a query and return all rows as a list of tuples"""
        query = self.execute_query(query_text, params)
        return self._rows_from_query(query) if query else []