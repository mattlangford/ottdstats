from openttd_stats import OpenTTDStats
from .openttd_interface import OpenTTDInterface
from jsonhelper import JsonHelper
import logginghelper
import requests

class OttdPoxyInterface(OpenTTDInterface):

    def __init__(self, openttd_server):
        OpenTTDInterface.__init__(self, openttd_server)

    def do_query(self):

        url = self.server.url
        post_data = JsonHelper.to_json({
            'payload': {
                'action': 'get'
            },
            'password': self.server.password
        })

        try:
            resp = requests.post(url, post_data)
        except requests.exceptions.Timeout:
            logginghelper.log_warning("Timeout while trying to contact " + self.server.name)
            return None
        except requests.exceptions.ConnectionException:
            logginghelper.log_warning("Error while contacting " + self.server.name)
            return None

        if not resp.status_code is 200:
            logginghelper.log_warning("Http Error " + str(resp.status_code) + " while connecting to " + self.server.name)
            return None

        resp_dict = JsonHelper.from_json(resp.text)

        if not 'status' in resp_dict:
            logginghelper.log_warning("Invalid response - no status - from " + self.server.name)
            return None

        if not resp_dict['status'] is 0:
            if 'error' in resp_dict:
                logginghelper.log_warning("Error received from Poxy on " + self.server.name +": '" + resp_dict['error'] + "'")
            else:
                logginghelper.log_warning("Unspecified error response from " + self.server.name)
            return None

        if not 'payload' in resp_dict:
            logginghelper.log_warning("Invalid response - no payload - from " + self.server.name)
        else:
            if not 'stats' in resp_dict['payload']:
                logginghelper.log_warning("Empty stats from " + self.server.name)
            else:
                stats = resp_dict['payload']['stats']

                ottd_stats = OpenTTDStats()
                ottd_stats.client_info = stats['client_info']
                ottd_stats.game_info = stats['game_info']
                ottd_stats.company_info = stats['company_info']

                return ottd_stats


        return None