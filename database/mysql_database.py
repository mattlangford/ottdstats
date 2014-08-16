import database
from database import Database

class MysqlDatabase(Database):

    def __init__(self):
        Database.__init__(self)
        pass
