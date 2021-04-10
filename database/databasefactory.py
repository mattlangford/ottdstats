from mysql.connector import MySQLConnection

class DatabaseFactory:

    @staticmethod
    def createdatabase(dbconfig):
        if dbconfig.type == "mysql":
            d = vars(dbconfig)
            d.pop("type")
            print (d)
            return MySQLConnection(**d)
        else:
            raise NotImplementedError(dbconfig.type + " is not implemented or not supported")
