from openttd_server import OpenTTDServer
from dbconfig import DbConfig
from general import GeneralConfig
from jsonhelper import JsonHelper
from os import path


class Config:
    __default_filename = "config.json"
    __full_path = ''

    def __init__(self, config_path='', dump_default=False):
        if config_path:
            Config.__full_path = config_path
        else:
            Config.__full_path = path.join(Config.__default_filename)

        if dump_default or not self.load():
            self.config = Config.__default()
            self.save()

    @property
    def servers(self):
        return [OpenTTDServer(**x) for x in self.config['config']['servers']]

    @property
    def database(self):
        return DbConfig(**self.config['config']['database'])

    @property
    def general(self):
        return GeneralConfig(**self.config['config']['general'])

    def load(self):
        try:
            self.config = JsonHelper.from_json_file(Config.__full_path)
            return True
        except IOError:
            return False

    def save(self):
        try:
            JsonHelper.to_json_file(self.config, Config.__full_path)
        except IOError:
            pass

    @staticmethod
    def __default():
        return {
                    "config":
                        {
                            "servers": [
                                {
                                    "name": "server1",
                                    "interface": "adminport",
                                    "host": "localhost",
                                    "port": 3977,
                                    "password": ""
                                },
                                {
                                    "name": "server2",
                                    "interface": "ottdpoxy",
                                    "url": "http://localhost:3017/stats",
                                    "password": ""
                                }
                            ],
                            "database": {
                                "type": "mysql",
                                "host": "localhost",
                                "port": 3306,
                                "username": "",
                                "password": "",
                                "database": "ottdstats"
                            },
                            "general": {
                                "daemon": False,
                                "interval": 30
                            }
                        }
                }
