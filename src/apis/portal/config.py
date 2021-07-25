try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

class Config(BaseConfig):
	def config_portal(self):
		self.app.config['PORTAL_MAX_PAGE_SIZE'] = 30

	def verify_portal(self):
		required_config = ['DATABASE_URL', 'PORTAL_MAX_PAGE_SIZE']
		
		return self._verify(required_config)