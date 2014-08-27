# This class represents state information derived from
from datetime import datetime
from openttd_stats import OpenTTDStats
from jsonhelper import JsonHelper
import logginghelper


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
            logginghelper.log_debug('ottdstats: Ending game number{0}'.format(self.current_game_id))

            db.execute("UPDATE game SET game_end = %(game_end)s, real_end = %(real_end) WHERE id = %(game_id)s",
                {
                    'real_end': datetime.now().isoformat(),
                    'game_end': self.last_snapshot.game_info['date'].isoformat(),
                    'game_id': self.current_game_id
                })
            for company_id in self.current_companies.copy():
                self.__end_company(db, self.current_companies[company_id]['id'])

            self.current_companies = {}
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
                clients = []
                for client in  new_snapshot.client_info:
                    if client['play_as'] == company_info['companyID']:
                        clients.append(client)
                if not company_info['companyID'] in self.current_companies:
                    self.__start_company(db, company_info, clients)
                else:
                    self.__update_company(db, company_info, clients)

        # create new game
        if self.current_game_id < 0:
            # time to create a new game.
            self.__start_game(db, new_snapshot)
            for company in new_snapshot.company_info:
                clients = []
                for client in  new_snapshot.client_info:
                    if client['play_as'] == company['companyID']:
                        clients.append(client)
                self.__start_company(db, company, clients)

        self.last_snapshot_time = datetime.now()
        self.last_snapshot = new_snapshot

        # temporary for testing
        JsonHelper.to_json_file({
            'company_info': self.last_snapshot.company_info,
            'game_info': self.last_snapshot.game_info,
            'client_info': self.last_snapshot.client_info
        }, "last_snapshot_sid" + str(self.server_id) + ".json")

        # save new state to db
        state = {
            'last_snapshot': self.last_snapshot.get_json(),
            'last_snapshot_time': self.last_snapshot_time.isoformat(),
            'game_id': self.current_game_id,
            'server_id': self.server_id
        }

        self.__insert_game_history(db, new_snapshot)

        db.execute("INSERT INTO state (server_id, last_snapshot, last_snapshot_time, game_id) "
            + "VALUES(%(server_id)s, %(last_snapshot)s, %(last_snapshot_time)s, %(game_id)s) "
            + "ON DUPLICATE KEY UPDATE last_snapshot=VALUES(last_snapshot),last_snapshot_time=VALUES(last_snapshot_time),"
            + "game_id=VALUES(game_id);", state)

    def __start_game(self, db, new_snapshot):
        game_info = new_snapshot.game_info
        insert = {
                    'server_id': self.server_id,
                    'game_start': game_info['date'].isoformat(),
                    'real_start': datetime.now().isoformat(),
                    'map_size_x': game_info['x'],
                    'map_size_y': game_info['y'],
                    'version': game_info['version'],
                    'landscape': game_info['landscape'],
                    'map_name': game_info['map_name'],
                    'seed': game_info['seed']
                }

        self.current_game_id = db.insert(
            'INSERT INTO game (server_id, game_start, real_start, map_size_x, map_size_y, version, landscape, map_name, seed) '
            'VALUES (%(server_id)s, %(game_start)s, %(real_start)s, %(map_size_x)s, %(map_size_y)s, %(version)s, %(landscape)s, '
            '%(map_name)s, %(seed)s)', insert)

    def __insert_game_history(self, db, new_snapshot):
        for company in new_snapshot.company_info:
            assert company['companyID'] in self.current_companies

            insert = {
                'game_id': self.current_game_id,
                'company_id': self.current_companies[company['companyID']]['id'],
                'current_company_name': company['name'],
                'current_company_manager':  company['manager'],
                'game_date': new_snapshot.game_info['date'].isoformat(),
                'real_date': datetime.now().isoformat(),
                'money': '-1',
                'value': '-1',
                'income': '-1',
                'loan': '-1',
                'delivered_cargo': -1,
                'station_bus': '-1',
            }

            if 'economy' in company:
                economy = company['economy']
                insert['money'] = economy['money']
                if len(economy['history']) > 0:
                    insert['value'] = economy['history'][0]['companyValue']
                insert['income'] = economy['income']
                insert['loan'] = economy['currentLoan']
                insert['delivered_cargo'] = economy['deliveredCargo']

            if 'stats' in company:
                stats = company['stats']
                stations = stats['stations']
                vehicles = stats['vehicles']
                insert['station_bus'] = stations['bus']
                insert['station_lorry'] = stations['lorry']
                insert['station_plane'] = stations['plane']
                insert['station_ship'] = stations['ship']
                insert['station_train'] = stations['train']
                insert['vehicle_bus'] = vehicles['bus']
                insert['vehicle_lorry'] = vehicles['lorry']
                insert['vehicle_plane'] = vehicles['plane']
                insert['vehicle_ship'] = vehicles['ship']
                insert['vehicle_train'] = vehicles['train']


            db.execute("INSERT INTO game_history (game_id, company_id, current_company_name, current_company_manager, "
                + "game_date, real_date, money, value, income, loan, delivered_cargo, station_bus, station_lorry, "
                + "station_ship, station_plane, station_train, vehicle_bus, vehicle_lorry, vehicle_ship, vehicle_plane, vehicle_train) "
                + "VALUES(%(game_id)s, %(company_id)s, %(current_company_name)s, %(current_company_manager)s, "
                + "%(game_date)s, %(real_date)s, %(money)s, %(value)s, %(income)s, %(loan)s, %(delivered_cargo)s, %(station_bus)s, %(station_lorry)s, "
                + "%(station_ship)s, %(station_plane)s, %(station_train)s, %(vehicle_bus)s, %(vehicle_lorry)s, %(vehicle_ship)s, %(vehicle_plane)s, %(vehicle_train)s)",
                   insert)

    def __insert_client(self, db, client, company_id):
        insert = {
                    'game_id': self.current_game_id,
                    'company_id': company_id,
                    'first_join': datetime.now().isoformat(),
                    'hostname': client['hostname'],
                    'client_id': client['clientID'],
                    'name': client['name']
                }

        db.insert('INSERT INTO game_company_client (game_id, company_id, first_join, hostname, client_id, name)'
            + ' VALUES (%(game_id)s, %(company_id)s, %(first_join)s, %(hostname)s, %(client_id)s, %(name)s)', insert)

    def __update_company(self, db, company_info, client_info):

        assert company_info['companyID'] in self.current_companies

        existing_company = self.current_companies[company_info['companyID']]
        for client in client_info:
            key = client['name'] + '|' + client['hostname']
            if key not in existing_company['clients']:
                existing_company['clients'][key] = client['clientID']
                self.__insert_client(db, client, existing_company['id'])

        if(True or not existing_company['name'] == company_info['name']
            or not existing_company['manager'] == company_info['manager']
            or not existing_company['color'] == company_info['colour']):
            existing_company['color'] = company_info['colour']
            existing_company['name'] = company_info['name']
            existing_company['manager'] = company_info['manager']

            update = {
                'game_id': self.current_game_id,
                'company_id': existing_company['id'],
                'color': company_info['colour'],
                'manager': company_info['manager'],
                'name': company_info['name']
            }

            db.execute(
                'UPDATE game_company SET color=%(color)s, manager=%(manager)s, name=%(name)s '
                    + 'WHERE game_id = %(game_id)s AND company_id = %(company_id)s', update)

    def __start_company(self, db, company_info, client_info):
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
        new_company['clients'] = {}
        for client in client_info:
            key = client['name'] + '|' + client['hostname']

            new_company['clients'][key] = client['clientID']
            self.__insert_client(db, client, new_company['id'])

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
            self.last_snapshot.client_info = snapshot['client_info']

            self.last_snapshot_time = state[cols['last_snapshot_time']]
            self.current_game_id = state[cols['game_id']]

            assert self.current_game_id > -1

            if self.current_game_id > -1:
                db.execute("SELECT * FROM game_company WHERE game_id = %(game_id)s AND end IS NULL",
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
                                'clients': {}
                            }

                        # load clients...
                        db.execute("SELECT * FROM game_company_client WHERE game_id = %(game_id)s AND "
                                   "company_id = %(company_id)s",  {'game_id': self.current_game_id, 'company_id': company[cols['id']]})
                        clients = db.fetch_results()
                        client_cols = db.columns()
                        if len(clients) > 0:
                            for client in clients:
                                key = client[client_cols['name']] + '|' + client[client_cols['hostname']]
                                self.current_companies[company_id]['clients'][key] = client[client_cols['client_id']]