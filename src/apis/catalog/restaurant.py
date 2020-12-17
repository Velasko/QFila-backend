from requests import get, exceptions

from flask import current_app
from flask_restx import Resource

from .app import api, ns

try:
	from ..utilities import headers
	from ..utilities.models.catalog import *
except ValueError:
	#If running from inside apis folder
	from utilities import headers
	from utilities.models.catalog import *

#meal, restaurant, foodcourt
for model in (meal, restaurant, foodcourt, catalog_response, catalog_restaurant_qtype):
	api.add_model(model.name, model)

@ns.route("/restaurant/<int:rest_id>/<string:qtype>/<string:keyword>")
class RestaurantMenu(Resource):

	@ns.doc(params={
		'rest_id' : "Restaurant's id to get data from.",
		'qtype' : "Type of search (name|foodtype|section)",
		'keyword' : "Keyword to search by"
	})
	@ns.response(200, 'Success. Returning meals', model=catalog_response)
	@ns.response(400, 'invalid qtype')
	@ns.response(503, 'Database unavailable')
	def get(self, rest_id, qtype, keyword):
		"""
		Queryies the internal restaurant's menu.

		possible qtypes:
			- Name
			- meal type (foodtype)
			- restaurant's category (section)
		"""

		try:
			resp = get("{}/database/catalog/restaurant/{}/{}/{}".format(
					current_app.config['DATABASE_URL'],
					rest_id, qtype, keyword
				),
				headers=headers.system_authentication
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		return resp.json(), 200

@ns.route("/restaurant/<int:rest_id>/<string:qtype>")
class RestaurantSections(Resource):

	@ns.doc(params={
		'rest_id' : "Restaurant's id to get data from.",
		'qtype' : "Type of search (foodtype|section)"
	})
	@ns.response(200, 'Success', model=catalog_restaurant_qtype)
	@ns.response(400, 'invalid qtype')
	@ns.response(503, 'Database unavailable')
	def get(self, rest_id, qtype):
		"""
		Fetches the restaurant's foodtypes or sections.

		possible qtypes:
			- meal type (foodtype)
			- restaurant's category (section)
		"""

		try:
			resp = get("{}/database/catalog/restaurant/{}/{}".format(
					current_app.config['DATABASE_URL'],
					rest_id, qtype
				),
				headers=headers.system_authentication
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		return resp.json(), resp.status_code