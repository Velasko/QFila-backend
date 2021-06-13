from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, user_methods, checkers, headers
	from ..utilities.models.client import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, user_methods, checkers, headers
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

		user_data = data['client']
		return user_methods.modify_user(
			client,
			'{}/database/client/{}/{}',
			data['old_password'],
			user_data
		)