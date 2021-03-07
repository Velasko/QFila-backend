try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

class Config(BaseConfig):
	def config_phone(self):
		self.limit_service_access('phone')

	def verify_phone(self):
		required_config = ['DATABASE_URL']
		
		return self._verify(required_config)