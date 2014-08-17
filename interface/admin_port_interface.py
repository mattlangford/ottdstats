from libottdadmin2.packets import *
from libottdadmin2.enums import *
from libottdadmin2.adminconnection import AdminConnection
from openttd_stats import OpenTTDStats
from openttd_interface import OpenTTDInterface
import select


class AdminPortInterface(OpenTTDInterface):

    def __init__(self, openttd_server):
        OpenTTDInterface.__init__(self, openttd_server)
        pass

    def do_query(self):

        connection = AdminConnection()

        connection.configure(
                name="ottdstats",
                host=self.server.host,
                port=self.server.port
        )

        if not connection.connect():
            raise "could not connect"
        try:
            connection.send_packet(AdminPoll,
                                            pollType = UpdateType.COMPANY_INFO,
                                            extra = PollExtra.ALL)
        except ValidationError:
            pass

        stats = OpenTTDStats()

        version = connection.recv_packet()
        welcome = connection.recv_packet()

        while True:
            # Todo: do this differently.
            available = select.select([connection], [], [], 0)

            if available[0]:
                result = connection.recv_packet()
                stats.company_info.append(result[1])
            else:
                break

        return stats