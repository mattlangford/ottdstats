from mysql import connector
from session import Session
from database import Database

class MysqlDatabase(Database):

    # Abstract this out someday.
    def __init__(self, config):
        Database.__init__(self, config)
        # self.upgrade()

    def connect(self):
        cnx = connector.connect(
            host=self.config.host,
            user=self.config.username,
            database=self.config.database,
            password=self.config.password)
        return Session(cnx)

    def upgrade(self):
        with self.connect() as session:
            session.begin()
            # do it.
            session.commit()

