import json

from datetime import date, datetime
from flask_restx import Resource, fields
from sqlalchemy import exc

from ..app import ns, session, api
from ..scheme import Base, User, FoodCourt, Restaurant, Meal, FoodType, Cart, OrderItem, safe_serialize, serialize

try:
	from ...utilities import checkers, authentication
	from ...utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers, authentication
	from utilities.models.user import *


#meal_info, rest, payment_model, order_contents, order -> history_response)
for model in (meal, restaurant, history, history_query, meal_info, rest, payment_model, order_contents, order, history_response):
	api.add_model(model.name, model)

@ns.route('/user/recents/<string:query_mode>/phone/<string:phone>')
@ns.route('/user/recents/<string:query_mode>/email/<string:email>')
class UserRecentsHandler(Resource):

	@ns.doc("Get user's recent meals or restaurants", params={'query_mode' : "Query mode must be 'meals' or 'restaurants'"})
	@ns.response(200, "Method executed successfully.", model=history)
	@ns.response(400, "Invalid payload")
	@ns.response(404, "Query type isn't neiter 'meals' nor 'restaurants'/invalid url")
	def get(self, query_mode, email=None, phone=None):
		"""Returns user recent meals/restaurants
		"""
		invalid_payload = {'message' : 'Invalid payload.'}
		try:
			data, field = get_data(email, phone)
		except KeyError:
			return invalid_payload, 400
		else:
			if session.query(User).filter(field == data).count() == 0:
				return invalid_payload, 400

		if query_mode == 'meals':
			initial_query = session.query(
					Meal
				).join(
					OrderItem,
					OrderItem.rest == Meal.rest and \
					OrderItem.meal == Meal.id
				)
		elif query_mode == 'restaurants':
			initial_query = session.query(
					Restaurant
				).join(
					OrderItem,
					OrderItem.rest == Restaurant.id
				)
		else:
			api.abort(404)

		query = initial_query.join(
			User,
			User.id == OrderItem.user
		).filter(
			field == data
		).order_by(
			OrderItem.time.desc()
		# ).distinct(
		# 	# Restaurant
		).limit(3)

		return {query_mode : [safe_serialize(rest) for rest in query.all()]}, 200


@ns.route('/user/history')
class HistoryHandler(Resource):

	@ns.expect(history_query)
	@ns.response(200, "Query executed successfully", model=history_response)	
	def post(self):

		user_id = api.payload['user']
		offset = api.payload.get('offset', 0)
		limit = api.payload.get('limit', 1)
		detailed = api.payload.get('detailed', True)
		time = api.payload.get('time', False)

		if time:
			time = datetime.fromisoformat(time)
			base_query = session.query(Cart).filter(Cart.user == user_id, Cart.time == time)
		else:
			base_query = session.query(Cart).filter(Cart.user == user_id)

		data = []
		for cart in base_query.order_by(Cart.time).offset(offset).limit(limit):
			cart = cart.serialize()
			del cart['user']
			cart['order'] = []

			meal_query = session.query(
				OrderItem, Meal.name
			).filter(
				OrderItem.user == user_id,
				OrderItem.time == cart['time']
			).join(
				Meal,
			)

			aux = {} #auxiliary variable to help separate by restaurant
			for meal, name in meal_query:
				meal = serialize(meal)
				rest = meal['rest']

				#removing redundant data
				del meal['time'], meal['user'], meal['rest']

				if not rest in aux:
					aux[rest] = []

				if detailed:
					meal['name'] = name

				aux[rest].append(meal) 

			for rest, order in aux.Orderitems():

				rest_data = {
					'rest' : rest,
					'meals' : order
				}

				if detailed:
					rest_data['name'], rest_data['image'] = session.query(
						Restaurant.name, Restaurant.image
					).filter(Restaurant.id == rest).first()


				cart['order'].append(rest_data)

			data.append(cart)

		return data