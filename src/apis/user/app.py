import datetime
import json
import jwt
import os

from functools import wraps

from requests import post, get, put, delete

from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse

#password

from werkzeug.security import check_password_hash, generate_password_hash

headers = {
	"accept": "application/json",
	"Content-Type": "application/json"
}

api = Api(version='0.1', title='Client',
	description='Client side interface',
)

ns = api.namespace('user', description='client operations')

user = api.model('User', {
	'email': fields.String(required=True, description='User email'),
	'passwd': fields.String(required=True, description='User password'),
})


def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):

		token = None

		if 'Token' in request.headers:
			token = request.headers['Token']

		if not token:
			return {'message': 'a valid token is missing'}

		try:
			data = jwt.decode(token, ns.app.config['SECRET_KEY'])
			resp = get(
				'{}/database/user'.format(ns.app.config['APPLICATION_HOSTNAME']),
				data=json.dumps({'email': data['email']}), headers=headers
			)
			current_user = resp.json()

			print(data)

		except jwt.ExpiredSignatureError as e:
			return {'message' : 'token expired'}
		except:
			return {'message': 'token is invalid'}

		#The self obj is actually the first item in args.
		#parsing "f(current_user, *args, **kwargs)" leads to a headache in the function 
		return f(args[0], current_user, *args[1:], **kwargs)
	return decorator


@ns.route("/login")
class Auth(Resource):

	@ns.doc("User authentication")
	@ns.expect(user)
	def get(self):
		"""Method to be authenticated"""
		# curl -X GET "http://localhost:5000/user/login" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"email\": \"vel3@app.com\", \"passwd\": \"string\" }"

		auth = api.payload

		resp = get(
			'{}/database/user'.format(ns.app.config['APPLICATION_HOSTNAME']),
			data=json.dumps({'email': auth['email']}), headers=headers
		)

		user = resp.json()

		if check_password_hash(user['passwd'], auth['passwd']):
			token = jwt.encode({
				'email' : user['email'],
				'exp' : datetime.datetime.utcnow() + datetime.timedelta(ns.app.config['session_ttl'])},
				ns.app.config['SECRET_KEY']
			)

			return {'token' : token.decode('UTF-8')}, 200
		else:
			return {}, 401

	# should this even be here?
	def update(self):
		"""Method to modify password?"""
		pass

	def post(self):
		"""method to create the login"""
		# curl -X POST "http://localhost:5000/user/login" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"name\": \"vel\",  \"email\": \"vel3@app.com\",  \"passwd\": \"string\",  \"birthday\": \"1980-08-25\",  \"phone\": 2}"
		data = api.payload

		for key, value in data.items():
			if key == 'passwd':
				data['passwd'] = generate_password_hash(data['passwd'], 'sha256')
			elif isinstance(value, str):
				data[key] = value.lower()

		resp = post(
			'{}/database/user'.format(ns.app.config['APPLICATION_HOSTNAME']),
			data=json.dumps(data), headers=headers
		)

	def delete(self):
		"""method to logout"""
		pass

#a test method for the required authentication
@ns.route("/test")
class User(Resource):

	@token_required
	def get(self, user):
		return user, 200




class Hist():
	# raise NotImplementedError("User purchase history not implemented")

	def post():
		"""A purchase has been made"""
		pass

	def get():
		"""Get purchase history"""
		pass

if __name__ == '__main__':
	app = Flask("Qfila user")
	api.init_app(app)
	app.run()