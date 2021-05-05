from requests import get, exceptions

from flask import request, current_app
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

parser = ns.parser()
parser.add_argument("page", type=int, default=1)
parser.add_argument("pagesize", type=int, default=-1)

@ns.route("/restaurant/<int:rest_id>/<string:qtype>/<string:keyword>")
class RestaurantMenu(Resource):

	@ns.doc(params={
		'rest_id' : "Restaurant's id to get data from.",
		'qtype' : "Type of search (name|foodtype|section)",
		'keyword' : "Keyword to search by",
		'page' : "Page to be fetched",
		'pagesize' : "The ammount of items to be fetched"
	})
	@ns.expect(parser)
	@ns.response(200, 'Success. Returning meals', model=catalog_response)
	@ns.response(400, 'invalid parsed')
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
			pagesize = int(request.args['pagesize'])
			if pagesize <= 0:
				pagesize = current_app.config['CATALOG_PAGE_SIZE_DEFAULT']

			limit = min(current_app.config['DATABASE_PAGE_SIZE_LIMIT'], pagesize)
			offset = (int(request.args['page']) - 1) * pagesize

			if offset < 0:
				raise TypeError
		except TypeError:
			return {'message' : 'invalid limit or pagesize'}, 400

		keyword = keyword.lower()

		try:
			resp = get("{}/database/catalog/restaurant/{}/{}/{}?limit={}&offset={}".format(
					current_app.config['DATABASE_URL'],
					rest_id, qtype, keyword, limit, offset
				),
				headers=headers.system_authentication
			)
		except exceptions.ConnectionError:
			return {'message': 'could not stablish connection to database'}, 503

		try:
			return resp.json(), 200
		except Exception:
			return {'message' : 'undexpected database response'}, 500

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