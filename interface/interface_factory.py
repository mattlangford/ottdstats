from interface import admin_port_interface
from interface import ottdpoxy_interface


class ServerInterfaceFactory:

    @staticmethod
    def createinterface(openttd_server):
        if openttd_server.interface == "adminport":
            return admin_port_interface.AdminPortInterface(openttd_server)
        if openttd_server.interface == "ottdpoxy":
            return ottdpoxy_interface.OttdPoxyInterface(openttd_server)
        else:
            raise NotImplementedError(openttd_server.interface + " is not implemented or not supported")