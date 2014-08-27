from libottdadmin2.packets import *
from libottdadmin2.enums import *
from libottdadmin2.adminconnection import AdminConnection
from openttd_stats import OpenTTDStats
from openttd_interface import OpenTTDInterface
import select
import logging

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
            logging.warning("Could not connect to " + self.server.name)
            return None

        # The order is important here - since the first poll (game_info) should return version / welcome
        stats = OpenTTDStats()
        stats.game_info = self.__poll_game_info(connection)
        stats.company_info = self.__poll_admin_array_info(connection, UpdateType.COMPANY_INFO, ServerCompanyInfo.packetID)
        stats.client_info = self.__poll_admin_array_info(connection, UpdateType.CLIENT_INFO, ServerClientInfo.packetID)
        company_stats = self.__poll_admin_array_info(connection, UpdateType.COMPANY_STATS, ServerCompanyStats.packetID)
        company_economy = self.__poll_admin_array_info(connection, UpdateType.COMPANY_ECONOMY, ServerCompanyEconomy.packetID)

        if company_stats:
            self.__match_company_stats(stats.company_info, company_stats)
        if company_economy:
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


        version = self.__poll_specific_packet(conn, ServerProtocol.packetID)
        if version is None:
            self.__packet_error('Protocol')

        game_info =  self.__poll_specific_packet(conn, ServerWelcome.packetID)
        if game_info is None:
            self.__packet_error('Welcome')

        game_date =  self.__poll_specific_packet(conn, ServerDate.packetID)
        if game_date is None:
            self.__packet_error('Date')
        game_info['date'] = game_date['date']

        return game_info

    def __poll_specific_packet(self, conn, packet_id):
        # Todo: do this differently.
        # No idea how much data is coming.
        # Poll is only unix..
        # the wait here is a hack since we might timeout before receiving it
        # so it may come back when we're not expecting
        while conn.is_connected:
            available = select.select([conn], [], [], 3)

            if available[0]:
                packet_type, packet = conn.recv_packet()
                if packet_type.packetID == packet_id:
                    return packet
            else:
                return None

    def __poll_admin_array_info(self, conn, update_type, receive_packet_id):
        array = []

        try:
            conn.send_packet(AdminPoll,
                                            pollType = update_type,
                                            extra = PollExtra.ALL)
        except ValidationError:
            return None

        while True:
            packet = self.__poll_specific_packet(conn, receive_packet_id)
            if not packet is None:
                array.append(packet)
            else:
                break

        return array

    def __packet_error(self, packet_name):
        # this is logged higher up the stack.
        # logging.error('admin_port_interface: Expected packet - ' + packet_name + ' - but never received.')
        raise Exception('Packet ' + packet_name + ' expected, but not found while listening on socket')