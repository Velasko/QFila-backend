import datetime
import re

from flask_restx import Resource, fields
from sqlalchemy import exc

from .app import ns, api, session
from .scheme import *

try:
	from ..utilities import payment
	from ..utilities.models.order import *
except ValueError:
	#If running from inside apis folder
	from utilities import payment
	from utilities.models.order import *

for model in (meal_info, rest, payment_model, order_contents, order, db_order):
	api.add_model(model.name, model)

@ns.route('/user/order')
class CartHandler(Resource):

	@ns.doc("Register order")
	@ns.expect(db_order)
	@ns.response(201, "Method executed successfully.")
	@ns.response(400, "Bad payload")
	@ns.response(409, "This order was already processed")
	def post(self):
		"""Register order"""

		#separating each meal
		order = []
		prices_per_rest = {}
		for data in api.payload['order']:
			restaurant = data['rest']

			meals = data['meals']
			for meal in meals:
				order.append({
					'rest' : restaurant,
					**meal
				})

			prices_per_rest[restaurant] = 0

		try:
			user = session.query(User).filter(User.email == api.payload['user']).first()
			time = datetime.datetime.fromisoformat(api.payload['time'])
			payment_method = api.payload['payment']['method']

			items = []
			compl_list = []
			for item_id, item_data in enumerate(order, start=1):
				meal = session.query(Meal).filter(Meal.id == item_data['meal'], Meal.rest==item_data['rest']).first()
				price = meal.price
				item_price = price * item_data.get('ammount', 1)

				prices_per_rest[item_data['rest']] += item_price

				complements = []
				if 'complements' in item_data:
					complements = item_data['complements']
					del item_data['complements']

				item = OrderItem(user=user.id, time=time, price=item_price, id=item_id, **item_data)
				items.append(item)

				for compl in complements:
					query = session.query(
						Complement, MealComplRel.ammount
					).join(
						MealComplRel,
						Complement.rest == MealComplRel.rest and \
						Complement.compl == MealComplRel.compl
					).filter(
						MealComplRel.meal  == item_data['meal'],
						MealComplRel.rest  == item_data['rest'],
						MealComplRel.compl == compl['id']
					).first()

					if query is None:
						return {'message': 'Invalid complement id'}, 400

					compl_data, multiplier = query

					#Verifying if complement items are within parameters
					if len(compl['items']) > compl_data.max * multiplier:
						return {'message' : 'too many complements'}, 400
					elif len(compl['items']) < compl_data.min * multiplier:
						return {'message' : 'lacking complements'}, 400
					elif any([ compl['items'].count(i) > compl_data.stackable * multiplier for i in compl['items'] ]):
						return {'message' : 'item overly selected'}, 400

					#Fetching items which are related to that meal
					items_query = session.query(
						ComplementItem
					).filter(
						ComplementItem.rest  == item_data['rest'],
						ComplementItem.compl == compl['id'],
						ComplementItem.name.in_(compl['items']),
						ComplementItem.available == 1
					).all()

					#verification for invalid requested items
					for compl_item in compl['items']:
						if not compl_item in items_query:
							return {'message' : f'Invalid "{compl_item}" item'}, 400
					# if any([i in items_query for i in compl['items'] ]):

					for compl_item in items_query:
						ammnt = compl['items'].count(compl_item.name)
						new_compl = OrderItemComplement(
							user=user.id,
							time=time,
							rest=item.rest,
							meal=item.meal,
							id=item.id,

							data=f"{ammnt} x {compl_item.name}",
							price=ammnt * compl_item.price
						)

						compl_list.append(new_compl)

						# restaurant bill += ammount of times of complement * complement price * ammount of times of the meal
						prices_per_rest[item.rest] += (ammnt * float(compl_item.price)) * item_data.get('ammount', 1)

			total_price = sum([value for rest, value in prices_per_rest.items()])
			fee = getattr(api.payload, 'fee', payment.service_fee(total_price))

			cart = Cart(time=time, user=user.id, price=total_price,
				payment_method=payment_method, qfila_fee=fee
			)
			session.add(cart)
			session.flush()

			for data in api.payload['order']:
				order = Order(user=user.id, time=time, rest=data['rest'],
					price=prices_per_rest[data['rest']], state='awaiting_payment', comment=data['comment']
				)
				session.add(order)
			session.flush()

			for item in items:
				session.add(item)
			session.flush()

			for compl in compl_list:
				session.add(compl)
			session.commit()

			return {}, 201
		except exc.IntegrityError as e:
			session.rollback()
			return {'message' : 'This order was already made'}, 409
		except exc.DataError as e:
			session.rollback()
			if "Data truncated for column \'payment_method\' at row 1" in e.args[0]:
				return {'message' : "Invalid payment method"}, 400
			raise(e)
		except Exception as e:
			session.rollback()
			raise e
			api.abort(500)