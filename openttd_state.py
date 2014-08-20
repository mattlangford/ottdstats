# This class represents state information derived from
from datetime import datetime
from openttd_stats import OpenTTDStats


class OpenTTDState:

    def __init__(self, server_id):
        self.server_id = server_id
        self.current_game_id = -1
        self.last_snapshot = []
        self.last_snapshot_time = datetime.now()

    def update(self, openttd_stats):
        self.last_snapshot_time = datetime.now()
        self.last_snapshot = openttd_stats
        # calculate delta between state
        # if snapshot date is less than state, create new game - save existing
        pass

    def save(self, db):
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
        if state.count(state) == 0:
            self.last_snapshot

        # load previous state from db
        pass
