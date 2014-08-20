import json
from datetime import datetime

class OpenTTDStats:
    def __init__(self):
        self.company_info = []
        self.game_info = {}
        self.player_info = []

    def get_json(self):
        return json.dumps({
            'company_info': self.company_info,
            'game_info': self.game_info,
            'player_info': self.player_info
        }, default=self.json_serial)

    def json_serial(self, obj):
        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial