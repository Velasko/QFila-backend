import datetime
import json
import jwt

from functools import wraps
from requests import get
from requests import exceptions as req_exc

from flask import request, current_app

#password hash
from argon2 import PasswordHasher, exceptions

from . import headers

HASHER = PasswordHasher()

class token_required():
	def __init__(self, namespace, *args, expect_args=[], expected_kwargs={}):
		self.ns = namespace
		self.expect_args = expect_args
		self.expected_kwargs = expected_kwargs

	def __call__(self, f):
		@wraps(f)
		def decorator(*args, **kwargs):
			token = None

			if 'Token' in request.headers:
				token = request.headers['Token']

			if not token:
				return {'message': 'Authentication required'}, 499

			try:
				data = jwt.decode(token, current_app.config['SECRET_KEY'])
			except jwt.ExpiredSignatureError as e:
				#token expired
				return {'message' : 'Token expired'}, 498
			except jwt.exceptions.DecodeError:
				return {'message' : 'Token invalid'}, 498

			if 'email' in data and not data['email'] is None:
				id_key = 'email'
			elif 'phone' in data and not data['phone'] is None:
				id_key = 'phone'
			else:
				return {'message' : 'Token invalid'}, 498

			try:
				resp = get(
					'{}/database/user/{}/{}'.format(
						current_app.config['DATABASE_URL'],
						id_key,
						data[id_key]
					),
					headers=headers.system_authentication
				)
				current_user = resp.json()
				current_user['id_key'] = id_key

				if current_user['passwd'] != data['passwd']:
					return {'message': 'Authentication required'}, 499

			except req_exc.ConnectionError:
				return {'message' : 'could not connect to database'}, 503
			# except Exception:
			# 	return {'message': 'Authentication required'}, 499

			#The self obj is actually the first item in args.
			#parsing "f(current_user, *args, **kwargs)" leads to a headache in the function 
			return f(args[0], current_user, *args[1:], **kwargs)

		if not self.ns is None:
			parser = self.ns.parser()
			parser.add_argument('token', help="Authentication token", location='headers')
			decorator = self.ns.expect(parser, *self.expect_args, **self.expected_kwargs)(decorator)
			decorator = self.ns.response(498, "Token expired or invalid")(decorator)
			decorator = self.ns.response(499, "Authentication required")(decorator)
			decorator = self.ns.response(503, "Servica unavailable. (Likely could not connect to database)")(decorator)

		return decorator


def passwd_check(user, auth_attempt, config=None):
	"""Function to check if the user authentication is correct.
	If valid: tries to generate a token; if fails returns True.

	If invalid: raises KeyError
	"""

	if config is None:
		config = current_app.config

	if isinstance(user, str):
		user_pass = user
		user_type = str
	else:
		user_type = dict
		user_pass = user['passwd']

	if isinstance(auth_attempt, str):
		auth_pass = auth_attempt
	else:
		auth_pass = auth_attempt['passwd']

	try:
		HASHER.verify(user_pass, auth_pass)

		if user_type == str:
			return True
		else:
			token = jwt.encode({
				'email' : user['email'],
				'phone' : user['phone'],
				'passwd' : user['passwd'],
				'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=config['session_ttl'])},
				config['SECRET_KEY']
			)

			return token.decode('UTF-8')

	except exceptions.VerifyMismatchError as e:
		raise KeyError('wrong password')

def generate_token(data, config, duration=None):
	"""This function generates a token with an expiration time.

	Arguments:
	 - data : dict. Data to be stored in token
	 - config. Must be the app's configuration dictionary
	 - duration : int (minutes) = App's default length. Can be parsed for a different value.
	"""

	if duration is None:
		duration = config['session_ttl']

	data['exp']  = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)
	token = jwt.encode(data, config['SECRET_KEY']).decode('UTF-8')
	return token

def hash_password(passwd):
	return HASHER.hash(passwd)
