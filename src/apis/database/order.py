import datetime
import re

from flask_restx import Resource, fields

from sqlalchemy import exc
from sqlalchemy.sql.expression import and_

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

				if meal.available == 0:
					# session.rollback()
					return {'message': 'One of the ordered meals is unavailable'}, 400

				price = meal.price
				item_price = price * item_data.get('ammount', 1)

				prices_per_rest[item_data['rest']] += item_price

				#handling complements:

				#getting all meal complements
				complements = session.query(
						Complement, MealComplRel.ammount
					).join(
						MealComplRel,
						and_(
							Complement.id == MealComplRel.compl,
							Complement.rest == MealComplRel.rest
						)
					).filter(
						MealComplRel.meal  == item_data['meal'],
						MealComplRel.rest  == item_data['rest'],
					)


				#required to create the item object in database
				order_complements = {}
				if 'complements' in item_data:
					# checking all the complements parsed in the order
					# are valid for their respective meal
					ids = [compl[0].id for compl in complements]
					if not all([compl['id'] in ids for compl in item_data['complements']]):
						return {'message' : 'invalid complement for one of the meals'}, 400

					order_complements = {compl['id'] : compl for compl in item_data['complements']}
					del item_data['complements']

				item = OrderItem(user=user.id, time=time, price=item_price, id=item_id, **item_data)
				items.append(item)

				for compl, ammount in complements:
					try:
						o_compl = order_complements[compl.id]
					except KeyError:
						if compl.min > 0:
							return {'message' : 'lacking complements'}, 400
						else:
							continue

					#Verifying if complement items are within parameters
					if len(o_compl['items']) > compl.max:
						return {'message' : 'too many complements'}, 400
					elif len(o_compl['items']) < compl.min:
						return {'message' : 'lacking complements'}, 400
					elif any([ o_compl['items'].count(i) > compl.stackable for i in o_compl['items'] ]):
						return {'message' : 'item overly selected'}, 400

					#Fetching items which are related to that meal
					items_query = session.query(
						ComplementItem
					).filter(
						ComplementItem.rest  == item_data['rest'],
						ComplementItem.compl == compl.id,
						ComplementItem.name.in_(o_compl['items']),
						ComplementItem.available == 1
					).all()

					#verification for invalid requested items
					for compl_item in o_compl['items']:
						if not compl_item in items_query:
							return {'message' : f'Invalid "{compl_item}" item'}, 400

					for compl_item in items_query:
						ammnt = o_compl['items'].count(compl_item.name)
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
			# session.rollback()
			return {'message' : 'This order was already made'}, 409
		except exc.DataError as e:
			# session.rollback()
			if "Data truncated for column \'payment_method\' at row 1" in e.args[0]:
				return {'message' : "Invalid payment method"}, 400
			raise(e)
		except Exception as e:
			# session.rollback()
			raise e
			api.abort(500)
		finally:
			session.rollback()