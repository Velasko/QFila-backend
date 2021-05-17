from requests import put, exceptions

from flask import current_app
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, checkers, headers
	from ..utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers
	from utilities.models.user import *

for model in (user, user_update):
	api.add_model(model.name, model)

@ns.route("/update")
class UserSettingsUpdate(Resource):

	@ns.doc("User information update")
	@authentication.token_required(namespace=ns, expect_args=[user_update])
	@ns.response(200, "Method executed successfully.")
	@ns.response(401, "Invalid password")
	@ns.response(400, "Query invalid.")
	@ns.response(403, "Birthday is less than 12 years ago.")
	@ns.response(409, "Email or phone already used.")
	def put(self, user):
		data = api.payload

		try:
			authentication.passwd_check(user['passwd'], data['old_password'])
		except KeyError:
			return {'message' : 'could not authenticate'}, 401

		if 'passwd' in data['user']:
			data['user']['passwd'] = authentication.hash_password(data['user']['passwd'])

		if 'phone' in data['user'] and (not re.fullmatch("+?([0-9]{9,14})", data['user']['phone']) is None):
					return {'message' : "Invalid phone number"}, 400

		resp = put('{}/database/user/{}/{}'.format(
				current_app.config['DATABASE_URL'],
				user['id_key'],
				user[user['id_key']]
			),
			json=data['user'],
			headers={**headers.json, **headers.system_authentication}
		)

		if resp.status_code == 404:
			# this shouldn't happen because token should be invalid
			# if there is no such user.
			return {'message' : 'Unexpected error'}, 500

		return resp.json(), resp.status_code