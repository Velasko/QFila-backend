import datetime
import json
import jwt

from functools import wraps
from requests import get

from flask import request

#password hash
from werkzeug.security import generate_password_hash, check_password_hash

headers = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

HASH_METHOD = 'sha256'

class token_required():
	def __init__(self, appmodule):
		#tried to use app directly, but a circular import error would pop up
		self.appmodule = appmodule

	def __call__(self, f):
		@wraps(f)
		def decorator(*args, **kwargs):
			token = None

			if 'Token' in request.headers:
				token = request.headers['Token']

			if not token:
				return {'message': 'a valid token is missing'}

			try:
				data = jwt.decode(token, self.appmodule.app.config['SECRET_KEY'])
				resp = get(
					'{}/database/user'.format(self.appmodule.app.config['DATABASE_URL']),
					data=json.dumps({'email': data['email']}), headers=headers
				)
				current_user = resp.json()

			except jwt.ExpiredSignatureError as e:
				return {'message' : 'token expired'}
			except TypeError:
				return {'message' : 'could not connect to database'}
			except:
				return {'message': 'token is invalid'}

			#The self obj is actually the first item in args.
			#parsing "f(current_user, *args, **kwargs)" leads to a headache in the function 
			return f(args[0], current_user, *args[1:], **kwargs)
		return decorator


def passwd_check(user, auth, config):

	#config expected to be app.config
	if check_password_hash(user['passwd'], auth['passwd']):
		token = jwt.encode({
			'email' : user['email'],
			'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=config['session_ttl'])},
			config['SECRET_KEY']
		)

		return token
	raise KeyError('invalid password')

def hash_password(passwd, hash=HASH_METHOD):
	return generate_password_hash(passwd, hash)
