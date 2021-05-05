import json
from datetime import date, datetime

from flask_restx import Resource, fields

from sqlalchemy import exc

from ..app import ns, session, api
from ..scheme import *

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


q_order_colmns = ['rest', 'price', 'rest_order_id']
q_compl_colmns = ['data', 'price']

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

			cart['orders'] = []			

			#for order in cart:
			for order in session.query(
				Order
			).filter(
				Order.user == user_id,
				Order.time == cart['time']
			):

				order = order.serialize()
				order['items'] = []

				#for item in order:
				for item in session.query(
					OrderItem
				).filter(
					OrderItem.user == user_id,
					OrderItem.time == cart['time'],
					OrderItem.rest == order['rest']
				):
					item = item.serialize()

					#item['complements'] = complements of that item
					item['complements'] = []
					for compl in session.query(
						OrderItemComplement
					).filter(
						OrderItemComplement.user == user_id,
						OrderItemComplement.time == cart['time'],
						OrderItemComplement.rest == order['rest'],
						OrderItemComplement.meal == item['meal'],
						OrderItemComplement.id == item['id']
					):
						compl = compl.serialize()
						for column in ['user', 'time', 'rest', 'meal', 'id']:
							del compl[column]
						item['complements'].append(compl)

					for column in ['user', 'time', 'rest', 'id', 'comments']:
						del item[column]
					order['items'].append(item)

				for column in ['user', 'time', 'comment']:
					del order[column]
				cart['orders'].append(order)

			data.append(cart)
		return data