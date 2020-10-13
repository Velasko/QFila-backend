import datetime
import json
import jwt

from functools import wraps
from requests import get

from flask import request, current_app

#password hash
from werkzeug.security import generate_password_hash, check_password_hash

from . import headers

HASH_METHOD = 'sha256'

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
				return {'message': 'Authentication required'}

			try:
				data = jwt.decode(token, current_app.config['SECRET_KEY'])
				resp = get(
					'{}/database/user'.format(current_app.config['DATABASE_URL']),
					data=json.dumps({'email': data['email']}), headers=headers.json
				)
				current_user = resp.json()

				if current_user['passwd'] != data['passwd']:
					raise Exception()

			except jwt.ExpiredSignatureError as e:
				#token expired
				return {'message' : 'Token expired'}, 498
			except TypeError:
				return {'message' : 'could not connect to database'}, 503
			except:
				return {'message': 'Authentication required'}, 499

			#The self obj is actually the first item in args.
			#parsing "f(current_user, *args, **kwargs)" leads to a headache in the function 
			return f(args[0], current_user, *args[1:], **kwargs)

		if not self.ns is None:
			parser = self.ns.parser()
			parser.add_argument('token', help="Authentication token", location='headers')
			decorator = self.ns.expect(parser, *self.expect_args, **self.expected_kwargs)(decorator)
			decorator = self.ns.response(498, "Token expired")(decorator)
			decorator = self.ns.response(499, "Authentication required")(decorator)
			decorator = self.ns.response(503, "Servica unavailable. (Likely could not connect to database)")(decorator)

		return decorator


def passwd_check(user, auth_attempt, config=None):
	"""Function to check if the user authentication is correct and returns a token
	if it is.

	Parameters:
	 - user : dict. Must contain 'email' and 'passwd' fields
	 - auth_attempt: dict. Must contain 'passwd' field.
	 - config: dict. Application's dictionary with it's secret key and session time to live.
	"""

	if config is None:
		config = current_app.config

	if check_password_hash(user['passwd'], auth_attempt['passwd']):
		token = jwt.encode({
			'email' : user['email'],
			'passwd' : user['passwd'],
			'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=config['session_ttl'])},
			config['SECRET_KEY']
		)

		return token.decode('UTF-8')
	raise KeyError('invalid password')

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

def hash_password(passwd, hash=HASH_METHOD):
	return generate_password_hash(passwd, hash)
