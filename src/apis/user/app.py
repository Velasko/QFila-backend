import datetime
import json
import jwt
import os

from functools import wraps

from requests import post, get, put, delete

from flask import Flask, request
from flask_restx import Api, Resource, fields, reqparse

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

try:
	from ..utilities import authentication, checkers, headers
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers

api = Api(version='0.1', title='Client',
	description='Client side interface',
)

ns = api.namespace('user', description='client operations')

user = api.model('User', {
	'email' : fields.String(required=True, description='User email'),
	'passwd' : fields.String(required=True, description='User password'),
})

new_user = api.inherit('New User', user, {
	'name' : fields.String(required=True, description='User name'),
    'birthday' : fields.DateTime(required=True, description='User birthday', dt_format="iso8601"),
    'phone' : fields.Integer(default=None, description='User phone number')
})


@ns.route("/login")
class Auth(Resource):

	@ns.doc("User authentication")
	@ns.expect(user)
	def get(self):
		"""Method to be authenticated"""
		# curl -X GET "http://localhost:5000/user/login" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"email\": \"f.l.velasko@gmail.com\", \"passwd\": \"string\" }"

		auth = api.payload

		user = get(
			'{}/database/user'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps({'email': auth['email']}), headers=headers.json
		).json()

		try:
			if ( token := authentication.passwd_check(user, auth, appmodule.app.config)):
				return {'token' : token}, 200
		except:
			api.abort(401, "Not authorized")

	# should this even be here?
	def update(self):
		"""Method to modify password?"""
		pass

	@ns.expect(new_user)
	def post(self):
		"""method to create the login"""
		# curl -X POST "http://localhost:5000/user/login" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"name\": \"vel\",  \"email\": \"vel3@app.com\",  \"passwd\": \"string\",  \"birthday\": \"1980-08-25\",  \"phone\": 2}"
		data = api.payload

		for key, value in data.items():
			if key == 'passwd':
				data['passwd'] = authentication.hash_password(data['passwd'])
			elif 'birthday' == value:
				date = date.fromisoformat(value)
				if not checkers.age_check(date):
					api.abort(403, "User below 12 years old")
			elif isinstance(value, str):
				data[key] = value.lower()
				if key == 'email' and not checkers.valid_email(value):
					api.abort(400, "Invalid email.")

		resp = post(
			'{}/database/user'.format(appmodule.app.config['DATABASE_URL']),
			data=json.dumps(data), headers=headers.json
		)

		return resp.json(), resp.status_code

	def delete(self):
		"""method to logout"""
		pass

#a test method for the required authentication
@ns.route("/test")
class User(Resource):

	@authentication.token_required(appmodule)
	def get(self, user):
		#curl -X GET "http://localhost:5000/user/test" -H "accept: application/json" -H  "Content-Type: application/json" -H "token: "
		return user, 200

from . import history

from . import password_recovery

if __name__ == '__main__':
	app = Flask("Qfila user")
	api.init_app(app)
	app.run()