from requests import put, exceptions

from flask import current_app
from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, checkers, headers
	from ..utilities.models.client import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, checkers, headers
	from utilities.models.client import *

for model in (client, client_update):
	api.add_model(model.name, model)

@ns.route("/update")
class ClientSettingsUpdate(Resource):

	@ns.doc("Client information update")
	@authentication.token_required(namespace=ns, expect_args=[client_update])
	@ns.response(200, "Method executed successfully.")
	@ns.response(401, "Invalid password")
	@ns.response(400, "Query invalid.")
	@ns.response(403, "Birthday is less than 12 years ago.")
	@ns.response(409, "Email or phone already used.")
	def put(self, client):
		data = api.payload

		try:
			authentication.passwd_check(client['passwd'], data['old_password'])
		except KeyError:
			return {'message' : 'could not authenticate'}, 401

		if 'passwd' in data['client']:
			data['client']['passwd'] = authentication.hash_password(data['client']['passwd'])

		if 'phone' in data['client'] and (not re.fullmatch("+?([0-9]{9,14})", data['client']['phone']) is None):
					return {'message' : "Invalid phone number"}, 400

		resp = put('{}/database/client/{}/{}'.format(
				current_app.config['DATABASE_URL'],
				client['id_key'],
				client[client['id_key']]
			),
			json=data['client'],
			headers={**headers.json, **headers.system_authentication}
		)

		if resp.status_code == 404:
			# this shouldn't happen because token should be invalid
			# if there is no such client.
			return {'message' : 'Unexpected error'}, 500

		return resp.json(), resp.status_code