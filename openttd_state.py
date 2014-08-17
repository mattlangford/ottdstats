# This class represents state information derived from

from openttd_stats import OpenTTDStats

class OpenTTDState:

    def __init__(self):
        self.companies = []

        pass

    def update(self, openttd_stats):

        # calculate delta between state
        pass

    def save(self, db):
        # save new state to db
        pass

    def load(self, db):
        # load previous state from db
        pass
