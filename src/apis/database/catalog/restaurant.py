from flask_restx import Resource

from flask import current_app

from ..app import ns, session, api
from ..scheme import Base, User, FoodCourt, Restaurant, MenuSection, Meal, FoodType, Cart, OrderItem, safe_serialize

from . import common

try:
	from ...utilities.models.catalog import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.catalog import *

for model in (compl_item, complement, meal, restaurant, foodcourt, catalog_response, catalog_restaurant_qtype):
	api.add_model(model.name, model)

@ns.route("/catalog/restaurant/<int:rest_id>/<string:qtype>/<string:keyword>")
class RestaurantMenu(Resource):

	@ns.doc(params={
		'page' : "Page to be fetched",
		'pagesize' : "The ammount of items to be fetched",
		'rest_id' : "Restaurant's id to get data from.",
		'qtype' : "Type of search (name|foodtype|section)",
		'keyword' : "Keyword to search by"
	})
	@ns.response(200, 'Success. Returning meals', model=catalog_response)
	@ns.response(400, 'invalid qtype')
	def get(self, rest_id, qtype, keyword, page=1, pagesize=None):
		"""
		Queryies the internal restaurant's menu.

		possible qtypes:
			- Name
			- meal type (foodtype)
			- restaurant's category (section)
		"""

		if pagesize is None:
			pagesize = current_app.config['CATALOG_PAGE_SIZE_DEFAULT']
		else:
			pagesize = int(pagesize)

		if qtype in ('name', 'foodtype'):
			query = session.query(
					Meal
				).filter(
					Meal.rest == rest_id,
					getattr(Meal, qtype).ilike(f"%{keyword}%")
				)

		elif qtype == 'section':
				query = session.query(
					Meal
				).join(
					MenuSection,
					MenuSection.meal == Meal.id and \
					MenuSection.rest == Meal.rest
				).filter(
					Meal.rest == rest_id,
					MenuSection.name == keyword
				)

		else:
			return {'message' : 'invalid qtype'}, 400


		limit = min(current_app.config['DATABASE_PAGE_SIZE_LIMIT'], pagesize)
		offset = (int(page) - 1) * pagesize
		query = query.offset(offset).limit(limit)

		response = { 'meal' : [safe_serialize(item) for item in query.all()]}

		common.fetch_meal_complements(response)

		return response

@ns.route("/catalog/restaurant/<int:rest_id>/<string:qtype>")
class RestaurantSections(Resource):

	@ns.doc(params={
		'rest_id' : "Restaurant's id to get data from.",
		'qtype' : "Type of search (foodtype|section)"
	})
	@ns.response(200, 'Success', model=catalog_restaurant_qtype)
	@ns.response(400, 'invalid qtype')
	def get(self, rest_id, qtype):
		"""
		Fetches the restaurant's foodtypes or sections.

		possible qtypes:
			- meal type (foodtype)
			- restaurant's category (section)
		"""		
		if qtype == 'foodtype':
			query = session.query(Meal.foodtype).filter(
				Meal.rest == rest_id
			)

		elif qtype == 'section':
			query = session.query(MenuSection.name).filter(
				MenuSection.rest == rest_id
			)

		else:
			return {'message' : 'invalid qtype'}, 400

		return { qtype : [item[0] for item in query.all()]}
