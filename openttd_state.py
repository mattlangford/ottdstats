# This class represents state information derived from
from datetime import datetime
from openttd_stats import OpenTTDStats
from jsonhelper import JsonHelper
import logging


class OpenTTDState:

    def __init__(self, server_id):
        self.current_companies = {}
        self.server_id = server_id
        self.current_game_id = -1
        self.last_snapshot = None
        self.last_snapshot_time = datetime.now()

    def update(self, db, new_snapshot):

        # game ends when the following condition is met:
        #   - Game date is older than last snapshot date
        if self.last_snapshot is not None and self.last_snapshot.game_info['date'] > new_snapshot.game_info['date']:
            logging.debug('ottdstats: Ending game number{0}'.format(self.current_game_id))
            db.execute("UPDATE game SET game_end = %(now)s WHERE game_id = %(game_id)s",
                {
                    'now': datetime.now().isoformat(),
                    'game_id': self.current_game_id
                })
            for company_id in self.current_companies.copy():
                self.__end_company(db, self.current_companies[company_id]['id'])

            self.current_companies = []
            self.current_game_id = -1

        # update existing game
        if self.current_game_id > -1:
            # check for companies that should be ended
            # Condition:
            # - company doesn't exist in snapshot, but existed in last
            found = False
            for company_id in self.current_companies.copy():
                found = False
                for company_info in new_snapshot.company_info:
                    if company_id == company_info['companyID']:
                        found = True
                        break
                if not found:
                    self.__end_company(db, self.current_companies[company_id]['id'])

            # check for companies that should be started
            for company_info in new_snapshot.company_info:
                if not company_info['companyID'] in self.current_companies:
                    self.__start_company(db, company_info)
                else:
                    self.__update_company(db, company_info)

        # create new game
        if self.current_game_id < 0:
            # time to create a new game.
            self.current_game_id = db.insert('INSERT INTO game (server_id, game_start) VALUES (%(server_id)s, %(game_start)s)',
                {
                    'server_id': self.server_id,
                    'game_start': self.last_snapshot_time.isoformat()
                })
            for company in new_snapshot.company_info:
                self.__start_company(db, company)

        self.last_snapshot_time = datetime.now()
        self.last_snapshot = new_snapshot

        # temporary for testing
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

        self.__insert_game_history(new_snapshot)

        db.execute("INSERT INTO state (server_id, last_snapshot, last_snapshot_time, game_id) "
            + "VALUES(%(server_id)s, %(last_snapshot)s, %(last_snapshot_time)s, %(game_id)s) "
            + "ON DUPLICATE KEY UPDATE last_snapshot=VALUES(last_snapshot),last_snapshot_time=VALUES(last_snapshot_time),"
            + "game_id=VALUES(game_id);", state)

    def __insert_game_history(self, new_snapshot):
        pass

    def __update_company(self, db, company_info):

        assert company_info['companyID'] in self.current_companies

        existing_company = self.current_companies[company_info['companyID']]
        if(not existing_company['name'] == company_info['name']
            or not existing_company['manager'] == company_info['manager']
            or not existing_company['color'] == company_info['colour']):
            existing_company['color'] = company_info['colour']
            existing_company['name'] = company_info['name']
            existing_company['manager'] = company_info['manager']

            db.execute(
                'UPDATE game_company SET color=%(color)s, manager=%(manager)s, name=%(name)s '
                    + 'WHERE game_id = %(game_id)s AND company_id = %(company_id)s', existing_company)

    def __start_company(self, db, company_info):
        new_company = {
            'game_id': self.current_game_id,
            'company_id': company_info['companyID'],
            'start': datetime.now().isoformat(),
            'name': company_info['name'],
            'color': company_info['colour'],
            'is_ai': company_info['isAI'],
            'manager': company_info['manager']
        }
        new_company['id'] = db.insert(
            'INSERT INTO game_company (game_id, company_id, start, name, manager, color, is_ai) '
            + 'VALUES(%(game_id)s, %(company_id)s, %(start)s, %(name)s, %(manager)s, %(color)s, %(is_ai)s)', new_company)

        assert not new_company['company_id'] in self.current_companies

        self.current_companies[new_company['company_id']] = new_company

    def __end_company(self, db, id):
        db.execute("UPDATE game_company SET end = %(now)s WHERE id = %(id)s",
                {
                    'now': datetime.now().isoformat(),
                    'id': id
                })
        for company_id in self.current_companies:
            if self.current_companies[company_id]['id'] == id:
                self.current_companies.pop(company_id)
                break

    def load(self, db):
        db.execute("SELECT * FROM state WHERE server_id = %(server_id)s", {'server_id': self.server_id})
        state = db.fetch_results()
        cols = db.columns()

        if len(state) == 1:
            state = state[0]
            snapshot = JsonHelper.from_json(state[cols['last_snapshot']])

            self.last_snapshot = OpenTTDStats()
            self.last_snapshot.company_info = snapshot['company_info']
            self.last_snapshot.game_info = snapshot['game_info']
            self.last_snapshot.player_info = snapshot['player_info']

            self.last_snapshot_time = state[cols['last_snapshot_time']]
            self.current_game_id = state[cols['game_id']]

            assert self.current_game_id > -1

            if self.current_game_id > -1:
                db.execute("SELECT * FROM game_company WHERE game_id = %(game_id)s",
                           {'game_id': self.current_game_id})
                companies = db.fetch_results()
                if len(companies) > 0:
                    cols = db.columns()
                    for company in companies:
                        company_id = company[cols['company_id']]
                        self.current_companies[company_id]= {
                                'id': company[cols['id']],
                                'game_id': company[cols['game_id']],
                                'company_id': company_id,
                                'start': company[cols['start']],
                                'color': company[cols['color']],
                                'manager': company[cols['manager']],
                                'name': company[cols['name']],
                            }