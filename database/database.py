from interface import admin_port_interface
import openttd_server


class Database:
    def __init__(self, config):
        self.config = config

    def connect(self):
        # todo: maybe provide more abstraction someday.

        pass