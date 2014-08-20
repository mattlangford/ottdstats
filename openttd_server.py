# class for storing specific openttd instance information

class OpenTTDServer:

    def __init__(self, **config_entries):
        self.__dict__.update(config_entries)
        self.id = -1