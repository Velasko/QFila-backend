from flask_restx import Resource
from flask import request, current_app

from sqlalchemy.sql.expression import and_

from ..app import DBsession, ns, api
from ..scheme import *

try:
	from ...utilities.models.catalog import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.catalog import *

for model in (compl_item, complement, meal, restaurant, foodcourt, catalog_response, catalog_restaurant_qtype):
	api.add_model(model.name, model)

parser = ns.parser()
parser.add_argument("offset", type=int)
parser.add_argument("limite", type=int)

@ns.route("/catalog/restaurant/<int:rest_id>/<string:qtype>/<string:keyword>")
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
	@ns.response(400, 'invalid qtype')
	@DBsession.wrapper
	def get(self, session, rest_id, qtype, keyword):
		"""
		Queryies the internal restaurant's menu.

		possible qtypes:
			- Name
			- meal type (foodtype)
			- restaurant's category (section)
		"""

		if qtype in ('name', 'foodtype'):
			query = session.query(
					Meal
				).filter(
					Meal.rest == rest_id,
					getattr(Meal, qtype).ilike(f"%{keyword}%"),
					Meal.available == 1
				).order_by(
					Meal.name
				)

		elif qtype == 'section':
				query = session.query(
					Meal
				).join(
					MenuSectionRelation,
					and_(MenuSectionRelation.meal == Meal.id,
					MenuSectionRelation.rest == Meal.rest)
				).filter(
					Meal.rest == rest_id,
					MenuSectionRelation.name.ilike(keyword),
					Meal.available == 1
				).order_by(
					MenuSectionRelation.position
				)

		else:
			return {'message' : 'invalid qtype'}, 400

		limit = request.args['limit']
		offset = request.args['offset']
		query = query.offset(offset).limit(limit)

		response = { 'meal' : [safe_serialize(item) for item in query]}

		return response

@ns.route("/catalog/restaurant/<int:rest_id>/<string:qtype>")
class RestaurantSections(Resource):

	@ns.doc(params={
		'rest_id' : "Restaurant's id to get data from.",
		'qtype' : "Type of search (foodtype|section)"
	})
	@ns.response(200, 'Success', model=catalog_restaurant_qtype)
	@ns.response(400, 'invalid qtype')
	@DBsession.wrapper
	def get(self, session, rest_id, qtype):
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
			).order_by(
				MenuSection.position
			)

		else:
			return {'message' : 'invalid qtype'}, 400

		return { qtype : [item[0] for item in query.distinct().all()]}