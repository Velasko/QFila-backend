from sqlalchemy.orm import sessionmaker, scoped_session

class SessionManager():
	def __init__(self, engine, *args, **kwargs):
		self._ssn_mkr = scoped_session(sessionmaker(bind=engine, *args, **kwargs))

	def __call__(self):
		return self._ssn_mkr()

	def wrapper(self, func):
		def wrapped(*args, **kwargs):
			with self as session:
				if len(args) == 0 or not func.__name__ in dir(args[0]):
					return func(session, *args, **kwargs)
				return func(args[0], session, *args[1:], **kwargs)
		return wrapped

	def __enter__(self):
		session = self._ssn_mkr()
		try:
			session.recursivity += 1
		except AttributeError:
			session.recursivity = 1

		return session

	def __exit__(self, *args):
		session = self._ssn_mkr()
		session.recursivity -= 1
		if session.recursivity == 0:
			self._ssn_mkr.remove()