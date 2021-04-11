from libottdadmin2.packets import *
from libottdadmin2.enums import *

from libottdadmin2.client.sync import OttdSocket, DefaultSelector
from libottdadmin2.constants import NETWORK_ADMIN_PORT

from openttd_stats import OpenTTDStats
from interface.openttd_interface import OpenTTDInterface
from jsonhelper import JsonHelper
import select
import logging

class AdminPortInterface(OpenTTDInterface):

    def __init__(self, openttd_server):
        OpenTTDInterface.__init__(self, openttd_server)
        self.messages = []

    def do_query(self):
        connection = OttdSocket(
            password=self.server.password,
        )
        self.selector = DefaultSelector()
        connection.register_to_selector(self.selector)

        def process_message(packet, data):
            print (f"Got packet: {packet}")
            self.messages.append((packet, data))
        connection.on_server_date_raw = process_message
        connection.on_server_protocol_raw = process_message
        connection.on_server_welcome_raw = process_message

        if not connection.connect((self.server.host, self.server.port)):
            logging.warning("Could not connect to " + self.server.name)
            raise Exception("Failed to connect")

        # The order is important here - since the first poll (game_info) should return version / welcome
        stats = OpenTTDStats()
        stats.game_info = self.__poll_game_info(connection)
        stats.company_info = self.__poll_admin_array_info(connection, UpdateType.COMPANY_INFO, ServerCompanyInfo.packet_id)
        stats.client_info = self.__poll_admin_array_info(connection, UpdateType.CLIENT_INFO, ServerClientInfo.packet_id)
        company_stats = self.__poll_admin_array_info(connection, UpdateType.COMPANY_STATS, ServerCompanyStats.packet_id)
        company_economy = self.__poll_admin_array_info(connection, UpdateType.COMPANY_ECONOMY, ServerCompanyEconomy.packet_id)

        if company_stats:
            self.__match_company_stats(stats.company_info, company_stats)
        if company_economy:
            self.__match_company_economy(stats.company_info, company_economy)

        connection.disconnect()

        # normalize values (convert to unicode)
        stats.game_info = JsonHelper.from_json(JsonHelper.to_json(stats.game_info))
        stats.company_info = JsonHelper.from_json(JsonHelper.to_json(stats.company_info))
        stats.client_info = JsonHelper.from_json(JsonHelper.to_json(stats.client_info))

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
            conn.send_packet(AdminPoll())
        except ValidationError:
            return None


        version = self.__poll_specific_packet(conn, ServerProtocol)
        if version is None:
            self.__packet_error('Protocol')

        game_info =  self.__poll_specific_packet(conn, ServerWelcome)
        if game_info is None:
            self.__packet_error('Welcome')

        game_date =  self.__poll_specific_packet(conn, ServerDate)
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
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

            for packet, data in self.messages:
                if isinstance(packet, packet_id):
                    print (f"Found! returning data: {data}")
                    return data

    def __poll_admin_array_info(self, conn, update_type, receive_packet_id):
        array = []

        try:
            conn.send_packet(AdminPoll())
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
