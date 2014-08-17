# class for storing specific openttd instance information

class OpenTTDServer:

    def __init__(self, **entries):
        self.__dict__.update(entries)