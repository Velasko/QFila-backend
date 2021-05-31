from flask import request

from flask_restx import Resource

from . import DBsession, api, ns
from .. import common
from ..scheme import *

try:
	from ...utilities import checkers
	from ...utilities.models.database import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers
	from utilities.models.database import *

for model in (restaurant,):
	api.add_model(model.name, model)

@ns.route('/user/phone/<string:login>')
@ns.route('/user/email/<string:login>')
class RestHandler(Resource):

	@ns.doc("Returns a restaurant based on it's login")
	@ns.response(200, "Method executed successfully", model=restaurant)
	@ns.response(404, "Restaurant not found")
	def get(self, login):
		"""Method to get Restaurant data based on it's login data"""

		path = request.full_path.split("/")
		return common.user.fetch_user(Restaurant, path[-2], login)