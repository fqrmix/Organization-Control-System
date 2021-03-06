import logging
import logging.config

from database.database_main import Database

logging.config.fileConfig('organization\employer\employer_log.conf')
logger = logging.getLogger("employerApp")

class Employer(object):
    def __init__(self):
        self.employer_database = Database('test DB')
        
    def get_employer_info(self, id):
        self.employer_info = self.employer_database.get_user_info(id)
        if self.employer_info is not None:
            return self.employer_info
        else: raise ValueError('ID is out of DB range!')
        
    def get_last_activity(self):
        print(f"Сотрудник {self.employer_info['name']} {self.employer_info['surname']} совершил действие '{self.employer_info['lastactivity']}'\n")
        logger.info(f"Сотрудник {self.employer_info['name']} {self.employer_info['surname']} совершил действие '{self.employer_info['lastactivity']}'\n")