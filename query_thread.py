import threading
import logginghelper


class QueryThread (threading.Thread):
    def __init__(self, interface, database, state):
        threading.Thread.__init__(self)
        self.threadID = interface.server.id
        self.interface = interface
        self.database = database
        self.state = state

    def run(self):
        self.__process_server()

    def __process_server(self):
        try:
            stats = self.interface.do_query()
            logginghelper.log_debug('Received stats from ' + self.interface.server.name)
            if stats is None:
                return
        except Exception as ex:
            logginghelper.log_error("Error trying to query server " + self.interface.server.name + ": " + ex.message)
            return

        try:
            with self.database.connect() as db_session:
                db_session.begin()
                restore_point = self.state.copy()
                try:
                    self.state.update(db_session, stats)
                    db_session.commit()
                    logginghelper.log_debug('Updated database for ' + self.interface.server.name)
                except Exception as ex:
                    db_session.rollback()
                    self.state.restore(restore_point)
                    logginghelper.log_error("Error updating database from query " + self.interface.server.name + ": " + ex.message)
        except Exception as ex:
            logginghelper.log_error("Error connecting to db while trying to update " + self.interface.server.name + ": " + ex.message)