import logging
import logging.config

from database.database_main import Database

logging.config.fileConfig('organization\organization_log.conf')
logger = logging.getLogger("organizationApp")

class Organization(object):
    def __init__(self):
        organization_database = Database('test DB')
        self.employers_list = organization_database.get_employers_list()
        if self.employers_list is not None:
            print (self.employers_list)
        else: raise ValueError('Organization is empty!')

    def get_organization_state(self):
        pass