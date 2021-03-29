from .shortner import url_cleanup_daemon

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

		url_cleanup_daemon()

		self.limit_service_access('database')