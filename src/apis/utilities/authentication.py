import datetime
import json
import jwt

from functools import wraps
from requests import get

from flask import request

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

#password hash
from werkzeug.security import generate_password_hash, check_password_hash

headers = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

HASH_METHOD = 'sha256'

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = None
		print("KEK IN token_required")

		if 'Token' in request.headers:
			token = request.headers['Token']

		if not token:
			return {'message': 'a valid token is missing'}

		try:
			data = jwt.decode(token, appmodule.app.config['SECRET_KEY'])
			resp = get(
				'{}/database/user'.format(appmodule.app.config['DATABASE_URL']),
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


def passwd_check(user, auth):
	if check_password_hash(user['passwd'], auth['passwd']):
		token = jwt.encode({
			'email' : user['email'],
			'exp' : datetime.datetime.utcnow() + datetime.timedelta(appmodule.app.config['session_ttl'])},
			appmodule.app.config['SECRET_KEY']
		)

		return token
	return False

def hash_password(passwd, hash=HASH_METHOD):
	generate_password_hash(data['passwd'], hash)
