import json
import re

from requests import post, get, exceptions

from flask import current_app
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, checkers, headers
	from ..utilities.models import database, login
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers
	from utilities.models import database, login

for model in (database.client, login.id, login.login_model, login.token):
	api.add_model(model.name, model)

@ns.route("/login")
class Authenticator(Resource):

	@ns.doc("Client authentication")
	@ns.expect(login.login_model)
	@ns.response(200, "Authentication successful", model=login.token)
	@ns.response(401, "Authentication failed")
	@ns.response(417, "Expected email or phone; got none.")
	@ns.response(503, "Could not stablish connection to database")
	def post(self):
		"""Method to be authenticated"""

		auth = api.payload
		path = "/database/client/{}/{}"

		return authentication.http_login(path, auth)


@ns.route("/register")
class Register(Resource):

	@ns.expect(database.client)
	@ns.response(201, "Client created")
	@ns.response(400, "Invalid payload; missing or invalid argument. Check 'missing' field.")
	@ns.response(403, "Born less than 12 years ago.")
	@ns.response(409, "Email or phone already used.")
	@ns.response(503, "Could not stablish connection to database")
	def post(self):
		"""method to create the client"""
		data = api.payload

		for key, value in data.items():
			if key == 'passwd':
				passwd = data['passwd']
				data['passwd'] = authentication.hash_password(passwd)

				try:
					authentication.passwd_check(data['passwd'], passwd)
				except KeyError:
					return {'message' : 'error in hashing password'}, 500

			elif 'birthday' == value:
				date = date.fromisoformat(value)
				if not checkers.age_check(date):
					return {'message' : "Client below 12 years old"}, 403

			elif isinstance(value, str):
				data[key] = value.lower()

				if key == 'email' and not checkers.valid_email(value):
					return {"missing" : "Invalid email."}, 400

				elif key == 'phone' and (re.fullmatch("\+?([0-9]{9,14})", value) is None):
					return {'message' : "Invalid phone number"}, 400

		try:
			resp = post(
				'{}/database/client/register'.format(current_app.config['DATABASE_URL']),
				data=json.dumps(data), headers={**headers.json, **headers.system_authentication}
			)

			if resp.status_code == 201:
				return {'message' : 'client created'}, 201
			elif resp.status_code in (400, 403, 409):
				return resp.json(), resp.status_code
			else:
				return {'message' : 'unexpected database behaviour'}, 500
		except exceptions.ConnectionError as e:
			return {'message': 'could not stablish connection to database'}, 503