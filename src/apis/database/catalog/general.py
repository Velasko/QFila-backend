import json

from flask import current_app
from flask_restx import Resource

from ..app import ns, session, api
from ..scheme import *

try:
	from ...utilities.models.catalog import *
except ValueError:
	#If running from inside apis folder
	from utilities.models.catalog import *

for model in (compl_item, complement, meal, restaurant, foodcourt, pagination_model, catalog_id_model, catalog_location, catalog_query, catalog_response):
	api.add_model(model.name, model)

@ns.route('/catalog')
class CatalogHandler(Resource):

	def get_order(self, qtype, location, limit=None):
		#Uses the user's location to calculate the food court's distances
		if qtype == 'location':
			order = self.get_foodcourt_order(**location, limit=limit)
		else:
			order = self.get_restaurant_order(**location, limit=limit)
		return order

	def get_foodcourt_order(self, city, state, longitude, latitude, limit=None):
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

	def get_restaurant_order(self, city, state, longitude, latitude, limit=None):
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

	def meal_id_query(self, **ids):
		"""A function to return meals based on it's ids.

		rest : int = the restaurant's id.
		meal : int list = the meal's id made by such restaurant.
				if meal is an empty list, all the restaurant's meals will be returned."""

		if ids['meal'] is None or ids['meal'] == []:
			return session.query(Meal).filter(Meal.rest.in_(ids['restaurant']))
		return session.query(Meal).filter(Meal.id.in_(ids['meal']), Meal.rest.in_(ids['restaurant']))

	def restaurant_id_query(self, **ids):
		"""A function to return restaurants based on it's ids.

		rest : int = the restaurant's id to be returned.
		foodcourt : int = The food court's id.
			if this argument is parsed, it will return every restaurant in it.
		"""

		if ids['restaurant'] is None:
			return session.query(Restaurant).filter(Restaurant.location.in_(ids['foodcourt']))
		return session.query(Restaurant).filter(Restaurant.id.in_(ids['restaurant']))

	def location_id_query(self, **ids):
		"""A function to return food courts based on it's ids.

		foodcourt : int = the foodcourt's id to be returned.
		"""

		return session.query(FoodCourt).filter(FoodCourt.id.in_(ids['foodcourt']))

#----------- Name Queries -----------#

	def base_name_query(self, db_class, rest_id, keyword, order):

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

	def meal_name_query(self, keyword, order):
		return self.base_name_query(db_class=Meal, rest_id=Meal.rest, keyword=keyword, order=order)

	def restaurant_name_query(self, keyword, order):
		return self.base_name_query(db_class=Restaurant, rest_id=Restaurant.id, keyword=keyword, order=order)

	def location_name_query(self, keyword, order):
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
	def get_types(self, keyword):
		return session.query(FoodType.name).filter(FoodType.name.ilike(keyword)).all()

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

	def fetch_meal_complements(self, response):
		for meal in response['meal']:
			complements = []
			meal['complements'] = complements

			compl_query = session.query(
				Complement, MealComplRel.ammount
			).join(
				MealComplRel,
				Complement.rest == MealComplRel.rest and \
				Complement.compl == MealComplRel.compl
			).filter(
				MealComplRel.meal == meal['id'],
				MealComplRel.rest == meal['rest']
			)

			for compl in compl_query:
				compl_data = serialize(compl[0])
				rest, compl_id = compl_data['rest'], compl_data['compl']

				item_query = session.query(
					ComplementItem
				).filter(
					ComplementItem.rest == rest,
					ComplementItem.compl == compl_id
				)

				compl_data['items'] = [{
					key: value for key, value in item.serialize().items()
						if key not in ('rest', 'compl')
				} for item in item_query]

				complements['max'] *= compl[1] #the ammount
				complements['min'] *= compl[1]
				complements.append(compl_data)

				del compl_data['rest'], compl_data['compl']

	@ns.expect(catalog_query)
	@ns.response(200, "Method executed successfully", model=catalog_response)
	@ns.response(404, "Couldn't find anything")
	def post(self):
		query_params = api.payload

		qtype = query_params['type']

		if query_params['category'] == 'id':
			kwargs = query_params['id']
		else:
			foodcourt_ammout = query_params['courts']
			location = query_params['location']
			kwargs = {
				'keyword': "%{}%".format(query_params['keyword']),
				'order' : self.get_order(qtype, location, limit=foodcourt_ammout)
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
			return {'message' : 'Nothing found'}, 404

		response = { query_params['type'] : [safe_serialize(Orderitem) for Orderitem in query.all()] }

		self.fetch_meal_complements(response)
		print('fetch_meal_complements finished')


		return json.dumps(response), 200