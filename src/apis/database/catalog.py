import json

from flask_restx import Resource

from .app import ns, session, api
from .scheme import Base, User, FoodCourt, Restaurant, Meal, FoodType, Cart, Item, safe_serialize

#getting the main app module
import importlib
appmodule = importlib.import_module(__package__.split('.')[0])

@ns.route('/catalog')
class CatalogHandler(Resource):

	def get_order(self, qtype, location):
		#Uses the user's location to calculate the food court's distances
		if qtype == 'location':
			order = self.get_foodcourt_order(**location)
		else:
			order = self.get_restaurant_order(**location)
		return order

	def get_foodcourt_order(self, city, state, longitude, latitude):
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

		return query.subquery()

	def get_restaurant_order(self, city, state, longitude, latitude):
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

		return query.subquery()

#----------- ID Queries -----------#

	def meal_id_query(self, **ids):
		"""A function to return meals based on it's ids.

		rest : int = the restaurant's id.
		meal : int list = the meal's id made by such restaurant.
				if meal is an empty list, all the restaurant's meals will be returned."""

		if ids['meal'] is None:
			return session.query(Meal).filter(Meal.rest == ids['restaurant'])
		return session.query(Meal).filter(Meal.id.in_(ids['meal']), Meal.rest == ids['restaurant'])

	def restaurant_id_query(self, **ids):
		"""A function to return restaurants based on it's ids.

		rest : int = the restaurant's id to be returned.
		foodcourt : int = The food court's id.
			if this argument is parsed, it will return every restaurant in it.
		"""

		if ids['restaurant'] is None:
			return session.query(Restaurant).filter(Restaurant.location == ids['foodcourt'])
		return session.query(Restaurant).filter(Restaurant.id == ids['restaurant'])

	def location_id_query(self, **ids):
		"""A function to return food courts based on it's ids.

		foodcourt : int = the foodcourt's id to be returned.
		"""

		return session.query(FoodCourt).filter(FoodCourt.id == ids['foodcourt'])

#----------- Name Queries -----------#

	def base_name_query(self, db_class, rest_id, keyword, order):

		query = session.query(
			db_class
		).join(
			order,
			rest_id == order.c.id #on
		).filter(
			db_class.name.like(keyword)
		).order_by(
			order.c.sort,
			db_class.name
		)

		return query

	def meal_name_query(self, keyword, order):
		return self.base_name_query(db_class=Meal, rest_id=Meal.rest, keyword=keyword, order=order)

	def restaurant_name_query(self, keyword, order):
		return self.base_name_query(db_class=Restaurant, rest_id=Restaurant.id, keyword=keyword, order=order)

	def location_name_query(self, keyword, order):
		query = session.query(
			FoodCourt
		).filter(
			FoodCourt.name.like(keyword)
		).join(
			order,
			FoodCourt.id == order.c.id
		).order_by(
			order.c.sort
		)

		return query

#----------- Type Queries -----------#
	def get_types(self, keyword):
		return session.query(FoodType.name).filter(FoodType.name.like(keyword)).all()

	def meal_type_query(self, keyword, order):

		types = self.get_types(keyword)	

		query = session.query(
			Meal
		).join(
			order,
			Meal.rest == order.c.id
		).filter(
			Meal.foodtype.in_([row[0] for row in types])
		).order_by(
			order.c.sort,
			Meal.name
		)

		return query

	def restaurant_type_query(self, keyword, order):
		types = self.get_types(keyword)		

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


	# @ns.expect(catalog_query)
	def get(self):
		query_params = api.payload

		location = query_params['location']
		qtype = query_params['type']


		if query_params['category'] == 'id':
			kwargs = query_params['id']
		else:
			kwargs = {
				'keyword': "%{}%".format(query_params['keyword']),
				'order' : self.get_order(qtype, location)
			}
		
		try:
			#Makes the query, ordered by the distances
			query = self.__getattribute__("{}_{}_query".format(
					query_params['type'],
					query_params["category"]
				)
			)(**kwargs)

		except KeyError as e:
			raise e

		except AttributeError as e:
			raise e
			api.abort(404)

		response = {
			'meal' : [],
			'restaurant' : [],
			'location' : []
		}

		offset = query_params['pagination']['offset']
		limit = min(appmodule.app.config['DATABASE_PAGE_SIZE_LIMIT'], query_params['pagination']['limit'])
		query = query.offset(offset).limit(limit)

		response[query_params['type']] = [ safe_serialize(item) for item in query.all() ]

		return json.dumps(response), 200