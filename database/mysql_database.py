from mysql import connector
from session import Session
from database import Database
from datetime import datetime
import logging
import logginghelper


class MysqlDatabase(Database):

    # To modify database
    # - increment below database_version variable
    # - append sql statements to script at the end of this class using new version

    # db changelog:
    #   1 - First version before release
    #   2 - Creating indexes
    #   3 - Create Client table
    #   4 - ???
    database_version = 3

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
            except Exception as ex:
                message = 'Could not create database: ' + ex.msg
                logging.error(message)
                raise Exception(message)

        cnx.database = self.config.database

        session = Session(cnx)

        # do it.
        session.execute("""
            CREATE TABLE IF NOT EXISTS upgrade_history (
              id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
              upgrade_date DATETIME,
              version INTEGER
            )""")

        session.execute("SELECT IFNULL(MAX(version),0) FROM upgrade_history")
        db_version = session.fetch_results()[0][0]  # first row first col

        script = self.__create_upgrade_script()

        max_version = 0
        for query in script:
            if query['version'] > db_version:
                if query['version'] > max_version:
                    max_version = query['version']
                session.execute(query['sql'])

        if max_version > db_version:
            session.execute("""INSERT INTO upgrade_history (upgrade_date, version)
                          VALUES('{date}', '{version}');""".format(date=datetime.now().isoformat(), version=max_version))
            logginghelper.log_debug('Upgraded database to version ' + str(max_version))

        session.commit()
        session.close()

    def __create_upgrade_script(self):
        sqls = []

        self.__append_upgrade_sql(
            r"""CREATE TABLE server (
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  name VARCHAR(100)
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
                  game_end DATETIME,
                  map_size_x INTEGER,
                  map_size_y INTEGER,
                  version VARCHAR(100),
                  landscape INTEGER,
                  map_name VARCHAR(100),
                  seed INTEGER
                );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE game_company(
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  game_id INTEGER NOT NULL,
                  company_id INTEGER NOT NULL,
                  start DATETIME,
                  end DATETIME,
                  name VARCHAR(100),
                  color INTEGER,
                  is_ai BOOLEAN,
                  manager VARCHAR(100)
                );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE game_history(
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  game_id INTEGER NOT NULL,
                  company_id INTEGER NOT NULL,
                  current_company_name VARCHAR(100) NOT NULL,
                  current_company_manager VARCHAR(100) NOT NULL,
                  game_date DATETIME,
                  real_date DATETIME,
                  money BIGINT,
                  value BIGINT,
                  income BIGINT,
                  loan INT,
                  delivered_cargo INT,
                  station_bus INT,
                  station_lorry INT,
                  station_ship INT,
                  station_plane INT,
                  station_train INT,
                  vehicle_bus INT,
                  vehicle_lorry INT,
                  vehicle_ship INT,
                  vehicle_plane INT,
                  vehicle_train INT
                );"""
            , 1, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_server_id ON game (
                  server_id
                );"""
            , 2, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_company_company_id ON game_company (
                  company_id
                );"""
            , 2, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_company_game_id ON game_company (
                  game_id
                );"""
            , 2, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_company_game_id_end ON game_company (
                  game_id,
                  end
                );"""
            , 2, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_history_game_id ON game_history (
                  game_id
                );"""
            , 2, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_history_company_id ON game_history (
                  company_id
                );"""
            , 2, sqls)

        self.__append_upgrade_sql(
            r"""CREATE TABLE game_company_client(
                  id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
                  game_id INTEGER NOT NULL,
                  company_id INTEGER NOT NULL,
                  first_join DATETIME,
                  hostname VARCHAR(100),
                  client_id INTEGER,
                  name VARCHAR(100)
                );"""
            , 3, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_company_client_game_id ON game_company_client (
                  game_id
                );"""
            , 3, sqls)

        self.__append_upgrade_sql(
            r"""CREATE INDEX idx_game_company_client_hostname ON game_company_client (
                  hostname
                );"""
            , 3, sqls)

        self.__append_upgrade_sql(
            r"""ALTER TABLE game ADD real_start DATETIME;"""
            , 3, sqls)

        self.__append_upgrade_sql(
            r"""ALTER TABLE game ADD real_end DATETIME;"""
            , 3, sqls)

        return sqls

    def __append_upgrade_sql(self, sql, version, sql_list):
        sql_list.append({'sql': sql, 'version': version})