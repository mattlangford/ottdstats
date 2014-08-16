# from libottdadmin2.trackingclient import poll, POLLIN, POLLOUT, POLLERR, POLLHUP, POLLPRI, POLL_MOD
# from libottdadmin2.constants import *
# from libottdadmin2.enums import *
# from libottdadmin2.packets import *
# from libottdadmin2.adminconnection import *
from libottdadmin2.client import AdminClient
from openttd_stats import OpenTTDStats
from openttd_interface import OpenTTDInterface

import socket


class AdminPortInterface(OpenTTDInterface):

    def __init__(self, openttd_server):
        OpenTTDInterface.__init__(openttd_server)
        pass

    def do_query(self):

        # Create a TCP/IP socket
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #
        # # Connect the socket to the port where the server is listening
        # server_address = ('localhost', 10000)
        #
        # # print >>sys.stderr, 'connecting to %s port %s' % server_address
        # sock.connect(server_address)
        #
        # conn = AdminConnection(sock)

        client = AdminClient()
        client.connect(self.server.host, self.server.port)

        stats = OpenTTDStats()
        return stats