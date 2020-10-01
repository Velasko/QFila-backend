try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

class Config(BaseConfig):
	def config_catalog(self):
		pass

	def verify_user(self):
		required_config = ['DATABASE_URL']
		
		return self._verify(required_config)