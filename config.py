from openttd_server import OpenTTDServer
from dbconfig import DbConfig
from general import GeneralConfig
from jsonhelper import JsonHelper


class Config:
    __filename = "config.json"

    def __init__(self):
        if not self.load():
            self.config = Config.__default()
            self.save()

    @property
    def servers(self):
        return map(lambda x: OpenTTDServer(**x), self.config['config']['servers'])

    @property
    def database(self):
        return DbConfig(**self.config['config']['database'])

    @property
    def general(self):
        return GeneralConfig(**self.config['config']['general'])

    def load(self):
        try:
            self.config = JsonHelper.from_json_file(Config.__filename)
            return True
        except IOError:
            return False

    def save(self):
        try:
            self.config = JsonHelper.to_json_file(self.config, Config.__filename)
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