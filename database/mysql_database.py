from mysql import connector
from session import Session
from database import Database
from datetime import datetime


class MysqlDatabase(Database):

    database_version = 1
    # Abstract this out someday.

    def __init__(self, config):
        Database.__init__(self, config)
        self.upgrade()

    def connect(self):
        cnx = connector.connect(
            host=self.config.host,
            user=self.config.username,
            database=self.config.database,
            password=self.config.password)
        return Session(cnx)

    def upgrade(self):
        cnx = connector.connect(
            host=self.config.host,
            user=self.config.username,
            password=self.config.password)

        db_cursor = cnx.cursor()

        db_cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{0}'".format(self.config.database))
        db_exists = db_cursor.fetchone()

        if not db_exists:
            try:
                db_cursor.execute("CREATE DATABASE {0}".format(self.config.database))
            except:
                raise Exception('Not able to create database. Please create manually.')

        cnx.database = self.config.database

        session = Session(cnx)

        # do it.
        session.execute("""
            CREATE TABLE IF NOT EXISTS upgrade_history (
              id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
              upgrade_date DATE,
              version INTEGER
            )""")

        session.execute("SELECT IFNULL(MAX(version),0) FROM upgrade_history")
        db_version = session.fetch_results()[0][0] # first row first col

        script = self.__create_upgrade_script()

        max_version = 0
        for query in script:
            if query['version'] > db_version:
                if query['version'] > max_version:
                    max_version = query['version']
                session.execute(query['sql'])

        if max_version > db_version:
            session.execute("""INSERT INTO upgrade_history (upgrade_date, version)
                          VALUES('{date}', '{version}');""".format(date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),version=max_version))

        session.commit()
        session.close()

    def __create_upgrade_script(self):
        sqls = []

        self.__append_upgrade_sql(
            r"""CREATE TABLE Server (
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  name VARCHAR(50)
                );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE state (
                  server_id INTEGER PRIMARY KEY NOT NULL,
                  last_snapshot TEXT,
                  last_snapshot_time DATETIME,
                  game_id INTEGER
            );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE game(
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  server_id INTEGER NOT NULL,
                  game_start DATETIME,
                  game_end DATETIME
                );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE game_company(
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  game_id INTEGER NOT NULL,
                  company_id INTEGER NOT NULL,
                  start DATETIME,
                  end DATETIME,
                  name VARCHAR(50),
                  color INTEGER,
                  is_ai BOOLEAN,
                  manager VARCHAR(50)
                );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE game_history(
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  game_id INTEGER NOT NULL,
                  company_id INTEGER NOT NULL,
                  game_date DATETIME,
                  real_date DATETIME,
                  money BIGINT,
                  income BIGINT,
                  loan INT,
                  delivered_cargo INT,
                  station_bus INT,
                  station_lorry INT,
                  station_ship INT,
                  station_train INT,
                  vehicle_bus INT,
                  vehicle_lorry INT,
                  vehicle_ship INT,
                  vehicle_train INT
                );"""
            , 1, sqls)

        return sqls

    def __append_upgrade_sql(self, sql, version, list):
        list.append({'sql': sql, 'version': version})

