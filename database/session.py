# this wraps a connection object so it can be more easily abstracted at some point

class Session:

    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def begin(self):
        self.conn.start_transaction()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def execute(self, statement, data=()):
        self.cursor.execute(statement, data)

    def insert(self, statement, data=()):
        self.execute(statement, data)
        return self.cursor.lastrowid

    def columns(self):
        cols = {}
        for idx, desc in enumerate(self.cursor.description):
            cols[desc[0]] = idx
        return cols

    def fetch_results(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()