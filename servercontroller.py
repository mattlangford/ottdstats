import time
from config import Config
from openttd_state import OpenTTDState
from interface.interface_factory import ServerInterfaceFactory
from database.databasefactory import DatabaseFactory
import logging


class ServerController:

    def __init__(self, startup={}):
        self.config = Config(startup['config_path'])
        self.interfaces = []
        self.server_states = {}
        self.database = None

    def start_server(self):
        self.database = DatabaseFactory.createdatabase(self.config.database)

        self.__create_server_interfaces()

        with self.database.connect() as db_session:
            self.__load_server_states(db_session)

        while True:
            for interface in self.interfaces:
                self.__process_server(interface)
            if not self.config.general.daemon:
                break
            time.sleep(self.config.general.interval)

    def __create_server_interfaces(self):
        servers = self.config.servers

        for server in servers:
            self.interfaces.append(ServerInterfaceFactory.createinterface(server))

    def __load_server_states(self, db):
        # find database server id
        db.execute("SELECT id, name FROM server;")
        db_servers = db.fetch_results()
        for interface in self.interfaces:
            server = interface.server

            for db_server in db_servers:
                if db_server[1] == server.name:
                    server.id = db_server[0]
                    break

            if server.id == -1:
                server.id = db.insert("INSERT INTO server (name) VALUES(%(name)s)", {'name': server.name})
                db.commit()

            # sanity check
            if not server.id in self.server_states:
                state = OpenTTDState(server.id)
                state.load(db)
                self.server_states[server.id] = state

    def __start_thread_loop(self):
        # at some point...
        pass

    def __process_server(self, interface):
        state = self.server_states[interface.server.id]

        try:
            stats = interface.do_query()
            if stats is None:
                return
        except Exception as ex:
            logging.error("Error trying to query server " + interface.server.name + ": " + ex.message)
            return

        try:
            with self.database.connect() as db_session:
                db_session.begin()
                try:
                    state.update(db_session, stats)
                    db_session.commit()
                except Exception as ex:
                    db_session.rollback()
                    logging.error("Error updating database from query " + interface.server.name + ": " + ex.message)
        except Exception as ex:
            logging.error("Error connecting to db while trying to update " + interface.server.name + ": " + ex.message)
