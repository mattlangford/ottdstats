import mysql_database


class DatabaseFactory:

    @staticmethod
    def createdatabase(type):
        if type == "mysql":
            return mysql_database.MysqlDatabase()
        else:
            raise NotImplementedError(type + " is not implemented or not supported")
