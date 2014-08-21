from jsonhelper import JsonHelper

class OpenTTDStats:
    def __init__(self):
        self.company_info = []
        self.game_info = {}
        self.player_info = []

    def get_json(self):
        return JsonHelper.to_json({
            'company_info': self.company_info,
            'game_info': self.game_info,
            'player_info': self.player_info
        })
