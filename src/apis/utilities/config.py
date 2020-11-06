import os

class BaseConfig():
	def __init__(self, app):
		self.app = app
		self._env = None

	def config_base(self):
		self.app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
		self.app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')
		self.app.config['session_ttl'] = 30

		#url.com/test/ and url.com/test will be the same with this argument:
		self.app.url_map.strict_slashes = False

		self.app.config['RESTX_VALIDATE'] = True #doesn't seems to be working

		self.app.config['TESTING'] = True
		self.app.config['ENV'] = 'development'

	def configure(self, auto_verify=True):
		"""Makes any execution required to configure the app"""
		for method in self.__dir__():
			if method.startswith("config_"):
				getattr(self, method)()

		if auto_verify:
			self.verify

	def verify(self):
		"""Method to verify if all the required configurations that
		can't be automated (such as urls assignment).

		Raises a KeyError if such configuration is not met.
		error.key can be used to retrieve the required parameter."""
		for method in self.__dir__():
			if method.startswith("verify_"):
				getattr(self, method)()

	def _verify(self, required_config):
		"""Base verification method."""
		for config in required_config:
			if not config in self.app.config or self.app.config[config] is None:
				error = KeyError(f"No {config} in app.config")
				error.key = config
				raise error


	def env_folder(self):
		if self._env is None:
			self._env = os.getenv("VIRTUAL_ENV") 
		return self._env