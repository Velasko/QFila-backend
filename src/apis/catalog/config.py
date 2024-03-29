try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

class Config(BaseConfig):
	def config_catalog(self):
		self.app.config['CATALOG_PAGE_SIZE_DEFAULT'] = 5
		self.app.config['CATALOG_PAGE_SIZE_LIMIT'] = 10

	def verify_user(self):
		required_config = ['DATABASE_URL']
		
		return self._verify(required_config)