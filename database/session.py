# this wraps a connection object so it can be more easily abstracted at some point

class Session:

    def __init__(self, conn):
        self.conn = conn
        #self.cursor = conn.cursor()

    def __enter__(self, conn):
        self.__init__(self, conn)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close();

    def begin(self):
        self.conn.start_transaction()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def execute(self, statement, data):
        return self.conn.execute(statement, data)

    def close(self):
        self.conn.close()