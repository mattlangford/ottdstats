from database.mysql_database import MysqlDatabase


class DatabaseFactory:

    @staticmethod
    def createdatabase(dbconfig):
        if dbconfig.type == "mysql":
            return MysqlDatabase(dbconfig)
        else:
            raise NotImplementedError(dbconfig.type + " is not implemented or not supported")
