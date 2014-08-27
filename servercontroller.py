import time
from config import Config
from openttd_state import OpenTTDState
from interface.interface_factory import ServerInterfaceFactory
from database.databasefactory import DatabaseFactory
from query_thread import QueryThread
import logginghelper

class ServerController:

    def __init__(self, startup={}):
        self.config = Config(startup['config_path'])
        self.interfaces = []
        self.server_states = {}
        self.database = None

    def start_server(self):
        logginghelper.log_info('Starting server as a ' + ('daemon' if self.config.general.daemon else 'script'))
        self.database = DatabaseFactory.createdatabase(self.config.database)

        self.__create_server_interfaces()

        with self.database.connect() as db_session:
            self.__load_server_states(db_session)

        self.__start_thread_loop()

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
        while True:
            threads = []
            for interface in self.interfaces:
                state = self.server_states[interface.server.id]
                thread = QueryThread(interface, self.database, state)
                thread.start()
                threads.append(thread)

            # wait for all threads
            for t in threads:
                t.join()

            if not self.config.general.daemon:
                break
            time.sleep(self.config.general.interval)


