import mysql.connector

class DatabaseFactory:

    @staticmethod
    def createdatabase(dbconfig):
        if dbconfig.type == "mysql":
            d = vars(dbconfig)
            d.pop("type")
            print (d)
            c = mysql.connector.connect(**d)
            if not c.is_connected():
                raise Exception("Can't connect to database")
            return c
        else:
            raise NotImplementedError(dbconfig.type + " is not implemented or not supported")
