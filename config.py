from openttd_server import OpenTTDServer
import json

class Config:
    __filename = "config.json"

    @property
    def servers(self):
        return map(lambda x: OpenTTDServer(**x), self.config['config']['servers'])

    @property
    def database(self):
        return self.config['config']['database'];

    def __init__(self):
        if not self.load():
            self.config = self.default()
            self.save()

    def load(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            return True
        except IOError:
            return False

    def save(self):
        try:
            with open(Config.__filename, 'w') as f:
                json.dump(self.config, f, sort_keys=True, indent=4)
        except IOError:
            pass

    def default(self):
        return {
                    "config":
                        {
                            "servers": [
                                {
                                    "id": "server1",
                                    "interface": "adminport",
                                    "host": "localhost",
                                    "port": 3977,
                                    "password": ""
                                }
                            ],
                            "database": {
                                "type": "mysql",
                                "host": "localhost",
                                "port": 0,
                                "username": "",
                                "password": "",
                                "database": "ottdstats"
                            }
                        }
                }