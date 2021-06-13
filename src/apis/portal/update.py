from flask_restx import Resource

from .app import ns, api

try:
	from ..utilities import authentication, user_methods, checkers, headers
	from ..utilities.models.portal import *
except ValueError:
	#If running from inside apis folder
	from utilities import authentication, user_methods, checkers, headers
	from utilities.models.portal import *

for model in (restaurant, rest_update):
	api.add_model(model.name, model)

@ns.route("/update")
class RestaurantSettingsUpdate(Resource):

	@ns.doc("Restaurant information update")
	@authentication.token_required(namespace=ns, expect_args=[rest_update])
	@ns.response(200, "Method executed successfully.")
	@ns.response(401, "Invalid password")
	@ns.response(400, "Query invalid.")
	@ns.response(409, "Email or phone already used.")
	def put(self, rest):
		data = api.payload

		user_data = data['rest']
		return user_methods.modify_user(
			rest,
			'{}/database/portal/user/{}/{}',
			data['old_password'],
			user_data
		)