import os

from flask import request

import threading
import asyncio

class BaseConfig(threading.Thread):
	def __init__(self, app):
		self.app = app
		self._env = None

		#Those are used to limit service access to the exterior
		self._keys = [] #on use keys
		self._blockedservices = [] #services secured

		super().__init__()
		self.daemon = True
		self._loop = asyncio.new_event_loop()

	def config_base(self):
		self.app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
		self.app.config['APPLICATION_HOSTNAME'] = os.getenv('APPLICATION_HOSTNAME')
		self.app.config['session_ttl'] = 24*60

		#url.com/test/ and url.com/test will be the same with this argument:
		self.app.url_map.strict_slashes = False

		self.app.config['RESTX_VALIDATE'] = True #doesn't seems to be working

		self.app.config['TESTING'] = True
		self.app.config['ENV'] = 'development'

		#limiting access
		for e in range(1, 4):
			key = os.getenv(f"SECURITY_HEADER{e}")
			if not key is None:
				self._keys.append(key)
		self.app.before_request(self.block_outside_requests)

		self.app.run = self.run_wrapper(self.app.run)
		self._tasks = []

	def configure(self, auto_verify=True):
		"""Makes any execution required to configure the app"""
		self.config_base()
		for method in self.__dir__():
			if method.startswith("config_") and method != 'config_base':
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

	def limit_service_access(self, service_name):
		self._blockedservices.append(service_name)

	def block_outside_requests(self):
		ns = request.full_path.split("/")[1]
		if ns in self._blockedservices:
			if not request.headers.get('security_header', False) in self._keys:
				return {"message": "Not authorized"}, 403

	def run_wrapper(self, run):
		def wrapped(*args, **kwargs):
			self.start()
			try:
				run(*args, **kwargs)
			finally:
				self.stop()
				pass

		return wrapped

	def coroutine_wrapper(self, function):
		async def wrapped(*args, **kwargs):
			try:
				return await function(*args, **kwargs)
			except asyncio.CancelledError:
				pass

		return wrapped

	def run(self):
		asyncio.set_event_loop(self._loop)
		self._loop.run_forever()

	def add_task(self, coroutine, *args, **kwargs):
		coro = self.coroutine_wrapper(coroutine)(*args, **kwargs)
		task = asyncio.run_coroutine_threadsafe(coro, self._loop)
		self._tasks.append(task)

	def stop(self, *args):
		for task in self._tasks:
			task.cancel()

		# import time
		# time.sleep(1)
		# self._loop.stop()