import time
from config import Config
from database import database
from openttd_state import OpenTTDState
from interface.interface_factory import ServerInterfaceFactory

class ServerController:

    def __init__(self):
        self.config = Config()
        self.interfaces = []
        self.server_states = {}

    def start_server(self):

        self.__create_server_interfaces()

        db = database.Database()
        db.connect()

        self.__load_server_states(db)

        db.disconnect()

        while True:
            for interface in self.interfaces:
                self.__process_server(interface)
            time.sleep(5)

    def __create_server_interfaces(self):
        servers = self.config.servers

        for server in servers:
            self.interfaces.append(ServerInterfaceFactory.createinterface(server))

    def __load_server_states(self, db):
        for interface in self.interfaces:
            server = interface.server
            # sanity check
            if not server.id in self.server_states:
                state = OpenTTDState()
                state.load(db)
                self.server_states[server.id] = state

    def __start_thread_loop(self):
        # at some point...
        pass

    def __process_server(self, interface):
        db = database.Database()
        db.connect()

        state = self.server_states[interface.server.id]
        stats = interface.do_query()

        state.update(stats)

        state.save(db)
