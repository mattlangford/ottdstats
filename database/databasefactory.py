import mysql_database


class DatabaseFactory:

    @staticmethod
    def createdatabase(dbconfig):
        if dbconfig.type == "mysql":
            return mysql_database.MysqlDatabase(dbconfig)
        else:
            raise NotImplementedError(dbconfig.type + " is not implemented or not supported")
