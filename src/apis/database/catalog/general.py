import json

from flask import current_app
from flask_restx import Resource

from sqlalchemy.sql.expression import case

from . import ns
from ..app import DBsession, api
from ..scheme import *

from . import common

try:
	from ...utilities.models.catalog import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.catalog import *

for model in (compl_item, complement, meal, restaurant, foodcourt, pagination_model, catalog_id_model, catalog_location, catalog_query, catalog_response):
	api.add_model(model.name, model)

@ns.route('/')
class CatalogHandler(Resource):

	def get_order(self, session, qtype, location, limit=None):
		#Uses the client's location to calculate the food court's distances
		if qtype == 'location':
			order = self.get_foodcourt_order(session, **location, limit=limit)
		else:
			order = self.get_restaurant_order(session, **location, limit=limit)
		return order

	def get_foodcourt_order(self, session, city, state, longitude, latitude, limit=None):
		query = session.query(
			FoodCourt.id.label('id'),
			((FoodCourt.longitude - longitude)*(FoodCourt.longitude - longitude) + \
			(FoodCourt.latitude - latitude)*(FoodCourt.latitude - latitude)).label('sort')
		).order_by(
			'sort'
		).filter(
			FoodCourt.city == city,
			FoodCourt.state == state
		)

		if not limit is None:
			query = query.limit(limit)

		return query.subquery()

	def get_restaurant_order(self, session, city, state, longitude, latitude, limit=None):
		"""Returns a list of tuples of the type (Restaurant.id as id, distance), based on
		the distance of longitude and latitude.

		City and state are used to filter the the possibility of restaurants.
		"""
		query = session.query(
			Restaurant.id.label('id'),
			((FoodCourt.longitude - longitude)*(FoodCourt.longitude - longitude) + \
			(FoodCourt.latitude - latitude)*(FoodCourt.latitude - latitude)).label('sort')
		).join(
			Restaurant,
			Restaurant.location == FoodCourt.id #on
		).order_by(
			'sort'
		).filter(
			FoodCourt.city == city,
			FoodCourt.state == state
		)

		if not limit is None:
			query = query.limit(limit)

		return query.subquery()

#----------- ID Queries -----------#

	def meal_id_query(self, session, **ids):
		"""A function to return meals based on it's ids.

		rest : int = the restaurant's id.
		meal : int list = the meal's id made by such restaurant.
				if meal is an empty list, all the restaurant's meals will be returned."""

		if ids['meal'] is None or ids['meal'] == []:
			return session.query(Meal).filter(Meal.rest.in_(ids['restaurant']))
		return session.query(Meal).filter(Meal.id.in_(ids['meal']), Meal.rest.in_(ids['restaurant']))

	def restaurant_id_query(self, session, **ids):
		"""A function to return restaurants based on it's ids.

		rest : int = the restaurant's id to be returned.
		foodcourt : int = The food court's id.
			if this argument is parsed, it will return every restaurant in it.
		"""

		if ids['restaurant'] is None or ids['restaurant'] == []:
			#sorting solution from https://stackoverflow.com/questions/21157513/sqlalchemy-custom-integer-sort-order
			# The order of restaurants must be based on the order of
			# the parsed food courts
			_whens = {key: n for n, key in enumerate(ids['foodcourt'])}

			query = session.query(
				Restaurant
			).filter(
				Restaurant.location.in_(
					ids['foodcourt']
				)
			).order_by(
				case(value=Restaurant.location, whens=_whens)
			)

			return query
		return session.query(Restaurant).filter(Restaurant.id.in_(ids['restaurant']))

	def location_id_query(self, session, **ids):
		"""A function to return food courts based on it's ids.

		foodcourt : int = the foodcourt's id to be returned.
		"""

		return session.query(FoodCourt).filter(FoodCourt.id.in_(ids['foodcourt']))

#----------- Name Queries -----------#

	def base_name_query(self, session, db_class, rest_id, keyword, order):

		query = session.query(
			db_class
		).join(
			order,
			rest_id == order.c.id #on
		).filter(
			db_class.name.ilike(keyword)
		).order_by(
			order.c.sort,
			db_class.name
		)

		return query

	def meal_name_query(self, session, keyword, order):
		return self.base_name_query(db_class=Meal, rest_id=Meal.rest, keyword=keyword, order=order).filter(Meal.available == 1)

	def restaurant_name_query(self, session, keyword, order):
		return self.base_name_query(db_class=Restaurant, rest_id=Restaurant.id, keyword=keyword, order=order)

	def location_name_query(self, session, keyword, order):
		query = session.query(
			FoodCourt
		).filter(
			FoodCourt.name.ilike(keyword)
		).join(
			order,
			FoodCourt.id == order.c.id
		).order_by(
			order.c.sort
		)

		return query

#----------- Type Queries -----------#
	def get_types(self, session, keyword):
		return session.query(FoodType.name).filter(FoodType.name.ilike(keyword)).all()

	def meal_type_query(self, session, keyword, order):

		types = self.get_types(session, keyword)

		query = session.query(
			Meal
		).join(
			order,
			Meal.rest == order.c.id
		).filter(
			Meal.foodtype.in_([row[0] for row in types]),
			Meal.available == 1
		).order_by(
			order.c.sort,
			Meal.name
		)

		return query

	def restaurant_type_query(self, session, keyword, order):
		types = self.get_types(session, keyword)

		query = session.query(
			Restaurant
		).join(
			order,
			Restaurant.id == order.c.id
		).join(
			Meal,
			Restaurant.id == Meal.rest
		).filter(
			Meal.foodtype.in_([row[0] for row in types])
		).order_by(
			order.c.sort,
			Restaurant.name
		)

		return query

	@ns.expect(catalog_query)
	@ns.response(200, "Method executed successfully", model=catalog_response)
	@ns.response(404, "Couldn't find anything")
	@DBsession.wrapper
	def post(self, session):
		query_params = api.payload

		qtype = query_params['type']

		if query_params['category'] == 'id':
			kwargs = {'session' : session, **query_params['id']}
		else:
			foodcourt_ammout = query_params['courts']
			location = query_params['location']
			kwargs = {
				'session' : session,
				'keyword': "%{}%".format(query_params['keyword']),
				'order' : self.get_order(session, qtype, location, limit=foodcourt_ammout)
			}
		
		try:
			#Makes the query, ordered by the distances
			query = self.__getattribute__("{}_{}_query".format(
					query_params['type'],
					query_params["category"]
				)
			)(**kwargs)

		except AttributeError as e:
			api.abort(404)

		response = {
			'meal' : [],
			'restaurant' : [],
			'location' : []
		}

		offset = query_params['pagination']['offset']
		limit = min(current_app.config['DATABASE_PAGE_SIZE_LIMIT'], query_params['pagination']['limit'])
		query = query.offset(offset).limit(limit)

		if query.count() == 0:
			return {'message' : 'Nothing found'}, 304

		response = { query_params['type'] : [safe_serialize(Orderitem) for Orderitem in query.all()] }

		if query_params['type'] == 'meal' and query_params["category"] == 'id':
			common.fetch_meal_complements(response)

		return json.dumps(response), 200