import sqlite3

class DatabaseManager:
    def __init__(self, db_name: str = "todo_list.db") -> None:
        self.db_name = db_name

    # Esegue una query che modifica il database (INSERT, UPDATE, DELETE)
    def execute_query(self, query: str, params: tuple = ()) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    # Esegue una query di SELECT e restituisce tutti i risultati
    def fetch_all(self, query: str, params: tuple = ()) -> list[tuple]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()