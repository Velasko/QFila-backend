import json

from requests import post, get, exceptions

from flask import current_app
from flask_restx import Resource
from flask_restx import Resource, fields

from .app import ns, api

try:
	from ..utilities import authentication, checkers, headers
	from ..utilities.models import database, user
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers
	from utilities.models import database, user

for model in (database.user, user.id, user.login_model, user.token):
	api.add_model(model.name, model)

@ns.route("/login")
class Authenticator(Resource):

	@ns.doc("User authentication")
	@ns.expect(user.login_model)
	@ns.response(200, "Authentication successful", model=user.token)
	@ns.response(401, "Authentication failed")
	@ns.response(417, "Expected email or phone; got none.")
	@ns.response(503, "Could not stablish connection to database")
	def post(self):
		"""Method to be authenticated"""
		# curl -X GET "http://localhost:5000/user/login" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"email\": \"f.l.velasko@gmail.com\", \"passwd\": \"string\" }"

		auth = api.payload

		if 'email' in auth:
			url = f'/database/user/email/{auth["email"]}'
		elif 'phone' in auth:
			url = f'/database/user/phone/{auth["phone"]}'
		else:
			return {'message' : "Id not parsed"}, 417 #change to proper code

		try:
			user = get(
				'{0}{1}'.format(current_app.config['DATABASE_URL'], url)
			).json()

			if ( token := authentication.passwd_check(user, auth, current_app.config)):
				return {'token' : token}, 200
		except KeyError as e:
			return {'message' : "Not authorized"}, 401

		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503



@ns.route("/register")
class Register(Resource):

	@ns.expect(database.user)
	@ns.response(201, "User created")
	@ns.response(400, "Invalid payload; missing or invalid argument. Check 'missing' field.")
	@ns.response(403, "Born less than 12 years ago.")
	@ns.response(409, "Email or phone already used.")
	@ns.response(503, "Could not stablish connection to database")
	def post(self):
		"""method to create the user"""
		# curl -X POST "http://localhost:5000/user/login" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"name\": \"Velasco\", \"email\": \"f.l.velasko@gmail.com\", \"passwd\": \"string\", \"birthday\": \"1997-04-30\", \"phone\": 0}"
		data = api.payload

		for key, value in data.items():
			if key == 'passwd':
				data['passwd'] = authentication.hash_password(data['passwd'])
			elif 'birthday' == value:
				date = date.fromisoformat(value)
				if not checkers.age_check(date):
					return {'message' : "User below 12 years old"}, 403
			elif isinstance(value, str):
				data[key] = value.lower()
				if key == 'email' and not checkers.valid_email(value):
					return {"missing" : "Invalid email."}, 400

		try:
			resp = post(
				'{}/database/user'.format(current_app.config['DATABASE_URL']),
				data=json.dumps(data), headers=headers.json
			)

			if resp.status_code == 201:
				return {'message' : 'user created'}
			elif resp.status_code in (400, 403, 409):
				return resp.json(), 400
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

#a test method for the required authentication
@ns.route("/test")
class User(Resource):

	@authentication.token_required(namespace=ns)
	def get(self, user):
		"""A simple token test, unofficial for the end system"""
		#curl -X GET "http://localhost:5000/user/test" -H "accept: application/json" -H  "Content-Type: application/json" -H "token: "
		return user, 200