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
                password=self.server.password,
                host=self.server.host,
                port=self.server.port
        )

        if not connection.connect():
            raise "could not connect"

        stats = OpenTTDStats()
        stats.game_info = self.__poll_game_info(connection)
        stats.company_info = self.__poll_admin_array_info(connection, UpdateType.COMPANY_INFO)
        stats.player_info = self.__poll_admin_array_info(connection, UpdateType.CLIENT_INFO)
        company_stats = self.__poll_admin_array_info(connection, UpdateType.COMPANY_STATS)
        company_economy = self.__poll_admin_array_info(connection, UpdateType.COMPANY_ECONOMY)

        self.__match_company_stats(stats.company_info, company_stats)
        self.__match_company_economy(stats.company_info, company_economy)

        connection.disconnect()

        return stats

    def __match_company_stats(self, companies, company_sub_info):

        for sub in company_sub_info:
            for comp in companies:
                if comp['companyID'] == sub['companyID']:
                    sub['stats'].pop("companyID", None)
                    comp['stats'] = sub['stats']
                    break

    def __match_company_economy(self, companies, company_sub_info):

        for sub in company_sub_info:
            for comp in companies:
                if comp['companyID'] == sub['companyID']:
                    sub.pop("companyID", None)
                    comp['economy'] = sub
                    break

    def __poll_game_info(self, conn):
        try:
            conn.send_packet(AdminPoll,
                                            pollType = UpdateType.DATE,
                                            extra = PollExtra.ALL)
        except ValidationError:
            return None

        version = conn.recv_packet()
        game_info = conn.recv_packet()[1]
        game_info['date'] = conn.recv_packet()[1]['date']

        return game_info

    def __poll_admin_array_info(self, conn, update_type):
        array = []

        try:
            conn.send_packet(AdminPoll,
                                            pollType = update_type,
                                            extra = PollExtra.ALL)
        except ValidationError:
            return None

        while conn.is_connected:
            # Todo: do this differently.
            # No idea how much data is coming.
            # Poll is only unix..
            # the wait here is a hack since we might timeout before receiving it
            # so it may come back when we're not expecting
            available = select.select([conn], [], [], 1)


            if available[0]:
                result = conn.recv_packet()
                array.append(result[1])
            else:
                break

        return array
