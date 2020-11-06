try:
	from ..utilities.config import *
except ValueError:
	#If running from inside apis folder
	from utilities.config import *

from .app import mail_scheduler

class Config(BaseConfig):
	def config_mail(self):
		self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
		self.app.config['MAIL_PORT'] = 587
		self.app.config['MAIL_USE_TLS'] = True
		self.app.config['MAIL_USE_SSL'] = False
		self.app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # enter your email here
		self.app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME') # enter your email here
		self.app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') # enter your password here

		mail_scheduler.init_app(self.app)

	def verify_mail(self):
		required_config = ['CATALOG_URL']
		
		return self._verify(required_config)