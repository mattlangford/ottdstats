from interface import admin_port_interface
import openttd_server


class Database:
    def __init__(self):
        pass

    def connect(self):
        # todo: correct connection pattern
        pass

    def disconnect(self):
        pass

    def get_server_interfaces(self):
        testinterface = admin_port_interface.AdminPortInterface(openttd_server.OpenTTDServer())
        return [testinterface]