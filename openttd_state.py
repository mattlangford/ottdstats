# This class represents state information derived from
from datetime import datetime
from openttd_stats import OpenTTDStats
from jsonhelper import JsonHelper


class OpenTTDState:

    def __init__(self, server_id):
        self.server_id = server_id
        self.current_game_id = -1
        self.last_snapshot = None
        self.last_snapshot_time = datetime.now()

    def update(self, db, openttd_stats):
        self.last_snapshot_time = datetime.now()
        new_game = False
        if self.last_snapshot != None and self.last_snapshot.game_info['date'] > openttd_stats.game_info['date']:
            # ending game. Use current date since we don't know time.
            db.execute("UPDATE game SET game_end = %(now)s WHERE game_id == %(game_id)s",
                {
                    'now': datetime.now().isoformat(),
                    'game_id': self.current_game_id
                })
            new_game = True

        if new_game or self.current_game_id < 0:
            # time to create a new game.
            self.current_game_id = db.insert('INSERT INTO game (server_id, game_start) VALUES (%(server_id)s, %(game_start)s)',
                {
                    'server_id': self.server_id,
                    'game_start': self.last_snapshot_time.isoformat()
                })

        self.last_snapshot = openttd_stats

        JsonHelper.to_json_file({
            'company_info': self.last_snapshot.company_info,
            'game_info': self.last_snapshot.game_info,
            'player_info': self.last_snapshot.player_info
        }, "test.json")

        # save new state to db
        state = {
            'last_snapshot': self.last_snapshot.get_json(),
            'last_snapshot_time': self.last_snapshot_time.isoformat(),
            'game_id': self.current_game_id,
            'server_id': self.server_id
        }

        db.execute("INSERT INTO state (server_id, last_snapshot, last_snapshot_time, game_id) "
            + "VALUES(%(server_id)s, %(last_snapshot)s, %(last_snapshot_time)s, %(game_id)s) "
            + "ON DUPLICATE KEY UPDATE last_snapshot=VALUES(last_snapshot),last_snapshot_time=VALUES(last_snapshot_time),"
            + "game_id=VALUES(game_id);", state)

    def load(self, db):
        db.execute("SELECT * FROM state WHERE server_id = %(server_id)s", {'server_id': self.server_id})
        state = db.fetch_results()
        cols = db.columns()
        if len(state) == 1:
            state = state[0]
            snapshot = state[cols['last_snapshot']]

            # todo - from json
            #self.last_snapshot = OpenTTDStats()
            #self.last_snapshot.company_info = snapshot['company_info']
            #self.last_snapshot.game_info = snapshot['game_info']
            #self.last_snapshot.player_info = snapshot['player_info']

            self.last_snapshot_time = state[cols['last_snapshot_time']]
            self.current_game_id = state[cols['game_id']]

