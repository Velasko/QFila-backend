try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

class Config(BaseConfig):
	def config_url_shortner(self):
		print("NOT IMPLEMENTED URL SHORTNER CONFIG")
		#must add the url which is used. client/phone service requires it.
		pass

	def verify_url_shortner(self):
		required_config = ['DATABASE_URL']

		return self._verify(required_config)