from interface import admin_port_interface


class ServerInterfaceFactory:

    @staticmethod
    def createinterface(type, openttd_server):
        if type == "adminport":
            return admin_port_interface.AdminPortInterface(openttd_server)
        else:
            raise NotImplementedError(type + " is not implemented or not supported")