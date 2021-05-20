import json
from datetime import date, datetime

from flask_restx import Resource, fields

from sqlalchemy import exc
from sqlalchemy.sql.expression import and_

from ..app import DBsession, ns, api
from ..scheme import *

try:
	from ...utilities import checkers, authentication
	from ...utilities.models.user import *
except ValueError:
	#If running from inside apis folder
	from utilities import checkers, authentication
	from utilities.models.user import *

for model in (recent_restaurant, recent_model, history_complements, history_items, history_order, history_response, history_query):
	api.add_model(model.name, model)

@ns.route('/user/recents/<int:user_id>')
class UserRecentsHandler(Resource):

	@ns.response(200, "Method executed successfully.", model=recent_model)
	@ns.response(400, "Invalid payload")
	@ns.response(404, "Query type isn't neiter 'meals' nor 'restaurants'/invalid url")
	def get(self, user_id):
		"""Returns user recent meals/restaurants
		"""
		with DBsession as session:
			query = session.query(
				Restaurant
			).join(
				Order,
				and_(
					Order.rest == Restaurant.id,
					Order.user == user_id
				)
			).order_by(
				Order.time.desc()
			).join(
				FoodCourt,
				Restaurant.location == FoodCourt.id
			).distinct(
			).limit(5)

			data = []
			for rest in query:
				fc = session.query(FoodCourt.name, FoodCourt.shopping).filter(FoodCourt.id == rest.location).first()
				r = {
					'id' : rest.id,
					'name' : rest.name,
					'image' : rest.image,
					'foodcourt_name' : fc[0],
					'shopping' : fc[1]
				}

				data.append(r)

			return {'restaurants' : data}, 200


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

		with DBsession as session:
			if time:
				time = datetime.fromisoformat(time)
				base_query = session.query(Cart).filter(Cart.user == user_id, Cart.time == time)
			else:
				base_query = session.query(Cart).filter(Cart.user == user_id)

			data = []
			for cart in base_query.order_by(Cart.time.desc()).offset(offset).limit(limit):
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

						for column in ['user', 'time', 'rest', 'id', 'comment']:
							del item[column]
						order['items'].append(item)

					for column in ['user', 'time', 'comment']:
						del order[column]
					cart['orders'].append(order)

				data.append(cart)
			return data