from flask import request

from flask_restx import Resource

from . import DBsession, api, ns
from .. import common
from ..scheme import *

try:
	from ...utilities import checkers
	from ...utilities.models import database, portal
except ValueError:
	#If running from inside apis folder
	from utilities import checkers
	from utilities.model import database, portal

for model in (database.restaurant, portal.restaurant):
	api.add_model(model.name, model)

@ns.route('/user/phone/<string:login>')
@ns.route('/user/email/<string:login>')
class RestHandler(Resource):

	@ns.doc("Returns a restaurant based on it's login")
	@ns.response(200, "Method executed successfully", model=database.restaurant)
	@ns.response(404, "Restaurant not found")
	def get(self, login):
		"""Method to get Restaurant data based on it's login data"""

		path = request.full_path.split("/")
		return common.user.fetch_user(Restaurant, path[-2], login)


	@ns.doc("Modify restaurant")
	@ns.expect(portal.restaurant)
	@ns.response(200, "Method executed successfully.")
	@ns.response(400, "Query invalid.")
	@ns.response(404, "Restaurant not found.")
	@ns.response(409, "Email or phone already used.")
	def put(self, login):
		"""Method to modify an client.

		The client identification must be parsed by the url, using either phone or email.
		The fields to be updated must be parsed on the payload.
		"""

		path = request.full_path.split("/")
		return common.user.update_user(Restaurant, path[-2], login, api.payload)