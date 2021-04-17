from .shortner_coroutine import url_cleanup

try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

class Config(BaseConfig):
	def config_database(self):
		#Database configuration
		self.app.config['DATABASE_URI'] = os.getenv('DATABASE_URI')
		self.app.config['DATABASE_PAGE_SIZE_DEFAULT'] = 5 
		self.app.config['DATABASE_PAGE_SIZE_LIMIT'] = 10

		self.add_task(url_cleanup())

		self.limit_service_access('database')